import asyncio
import time
from typing import Any, Dict

import pytest
from starlette.websockets import WebSocketDisconnect

from excars import repositories
from excars.models.locations import Location, MapItem
from excars.models.messages import MessageType
from excars.models.profiles import Role
from excars.models.rides import RideRequest, RideRequestStatus


def assert_map_item(message: Dict[str, Any], user_id: int, location: Location, has_same_ride: bool):
    assert message["type"] == MessageType.map
    map_item = MapItem(**message["data"][0])
    assert map_item.user_id == user_id
    assert map_item.location.user_id == user_id
    assert map_item.location.latitude == location.latitude
    assert map_item.location.longitude == location.longitude
    assert map_item.has_same_ride == has_same_ride


def wait_for_message_type(ws, message_type: MessageType, count: int = 3):
    result = False
    for _ in range(count):
        data = ws.receive_json()
        if data["type"] == message_type:
            result = True
    return result


def test_ws_close_for_unauthorized_user(client):
    with pytest.raises(WebSocketDisconnect):
        with client as cli, cli.websocket_connect("/api/v1/ws") as ws:
            ws.receive_json()


def test_ws_receive_empty_map(client, make_token_headers):
    with client as cli, cli.websocket_connect("/api/v1/ws", headers=make_token_headers()) as ws:
        data = ws.receive_json()
        assert data == {"type": MessageType.map, "data": []}


@pytest.mark.parametrize("role", [Role.driver, Role.hitchhiker])
def test_ws_receive_map_for_user_without_ride(client, location_factory, profile_factory, make_token_headers, role):
    sender = profile_factory(role=role)
    location = location_factory(user_id=sender.user_id)

    receiver = profile_factory(role=Role.opposite(role))
    location_factory(user_id=receiver.user_id)

    with client as cli:
        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(receiver.user_id)) as ws:
            assert_map_item(ws.receive_json(), sender.user_id, location, has_same_ride=False)


@pytest.mark.parametrize("role", [Role.driver, Role.hitchhiker])
def test_ws_receive_map_without_ride_and_profile(client, location_factory, profile_factory, make_token_headers, role):
    sender = profile_factory(role=role)
    location = location_factory(user_id=sender.user_id)

    receiver_user_id = sender.user_id + "1"
    location_factory(user_id=receiver_user_id)

    with client as cli:
        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(receiver_user_id)) as ws:
            assert_map_item(ws.receive_json(), sender.user_id, location, has_same_ride=False)


def test_ws_receive_no_map_without_profile(client, faker, location_factory, make_token_headers):
    receiver_user_id = faker.pyint()
    location_factory(user_id=receiver_user_id)
    location_factory()

    with client as cli:
        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(receiver_user_id)) as ws:
            data = ws.receive_json()
            assert data == {"type": MessageType.map, "data": []}


@pytest.mark.parametrize("role", [Role.driver, Role.hitchhiker])
def test_ws_receive_map_within_same_ride(client, location_factory, profile_factory, make_token_headers, role):
    ride_request = RideRequest(
        sender=profile_factory(role=role),
        receiver=profile_factory(role=Role.opposite(role)),
        status=RideRequestStatus.accepted,
    )
    location = location_factory(user_id=ride_request.sender.user_id)
    location_factory(user_id=ride_request.receiver.user_id)

    with client as cli:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(repositories.rides.update_request(cli.app.redis_cli, ride_request))

        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(ride_request.receiver.user_id)) as ws:
            assert_map_item(ws.receive_json(), ride_request.sender.user_id, location, has_same_ride=True)


@pytest.mark.parametrize("role", [Role.driver, Role.hitchhiker])
def test_ws_receive_map_within_different_ride(client, location_factory, profile_factory, make_token_headers, role):
    ride_request = RideRequest(
        sender=profile_factory(role=role),
        receiver=profile_factory(role=Role.opposite(role)),
        status=RideRequestStatus.accepted,
    )
    location_factory(user_id=ride_request.receiver.user_id)

    receiver = profile_factory(role=role)
    location_factory(user_id=receiver.user_id)

    with client as cli:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(repositories.rides.update_request(cli.app.redis_cli, ride_request))

        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(receiver.user_id)) as ws:
            assert ws.receive_json() == {"type": MessageType.map, "data": []}


def test_ws_send_location(client, profile_factory, make_token_headers):
    sender = profile_factory(role=Role.driver)

    with client as cli:
        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(sender.user_id)) as ws:
            ws.send_json({"type": MessageType.location, "data": {"longitude": 1, "latitude": 1, "course": -1}})


def test_ws_send_invalid_data(client, profile_factory, make_token_headers):
    sender = profile_factory(role=Role.driver)

    with client as cli:
        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(sender.user_id)) as ws:
            ws.send_json({"type": MessageType.location, "data": {"longitude": 1}})
            message = ws.receive_json()
            assert message["type"] == MessageType.error
            assert isinstance(message["data"], list)


def test_ws_receive_ride_requested(client, profile_factory, make_token_headers):
    ride_request = RideRequest(
        sender=profile_factory(role=Role.driver),
        receiver=profile_factory(role=Role.hitchhiker),
        status=RideRequestStatus.requested,
    )

    with client as cli:
        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(ride_request.receiver.user_id)) as ws:
            time.sleep(0.1)
            loop = asyncio.get_event_loop()
            loop.create_task(repositories.stream.ride_requested(cli.app.redis_cli, ride_request))
            assert wait_for_message_type(ws, MessageType.ride_requested)


@pytest.mark.parametrize(
    "status,expected",
    [
        (RideRequestStatus.accepted, MessageType.ride_request_accepted),
        (RideRequestStatus.declined, MessageType.ride_request_declined),
    ],
)
def test_ws_receive_ride_request_updated(client, profile_factory, make_token_headers, status, expected):
    ride_request = RideRequest(
        sender=profile_factory(role=Role.driver), receiver=profile_factory(role=Role.hitchhiker), status=status
    )

    with client as cli:
        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(ride_request.sender.user_id)) as ws:
            time.sleep(0.1)
            loop = asyncio.get_event_loop()
            loop.create_task(repositories.stream.request_updated(cli.app.redis_cli, ride_request))
            assert wait_for_message_type(ws, expected)


@pytest.mark.parametrize("role", [Role.driver, Role.hitchhiker])
def test_ws_ride_updated(client, profile_factory, make_token_headers, role):
    ride_request = RideRequest(
        sender=profile_factory(role=role),
        receiver=profile_factory(role=Role.opposite(role)),
        status=RideRequestStatus.accepted,
    )

    with client as cli:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(repositories.rides.update_request(cli.app.redis_cli, ride_request))
        ride_id = loop.run_until_complete(
            repositories.rides.get_ride_id(cli.app.redis_cli, ride_request.sender.user_id)
        )
        ride = loop.run_until_complete(repositories.rides.get(cli.app.redis_cli, ride_id))

        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(ride_request.sender.user_id)) as ws:
            time.sleep(0.1)
            loop.create_task(repositories.stream.ride_updated(cli.app.redis_cli, ride))
            assert wait_for_message_type(ws, MessageType.ride_updated)


def test_ws_ride_cancelled(client, profile_factory, make_token_headers):
    ride_request = RideRequest(
        sender=profile_factory(role=Role.driver),
        receiver=profile_factory(role=Role.hitchhiker),
        status=RideRequestStatus.accepted,
    )

    with client as cli:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(repositories.rides.update_request(cli.app.redis_cli, ride_request))
        ride_id = loop.run_until_complete(
            repositories.rides.get_ride_id(cli.app.redis_cli, ride_request.sender.user_id)
        )
        ride = loop.run_until_complete(repositories.rides.get(cli.app.redis_cli, ride_id))

        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(ride_request.receiver.user_id)) as ws:
            time.sleep(0.1)
            loop.create_task(repositories.stream.ride_cancelled(cli.app.redis_cli, ride))
            assert wait_for_message_type(ws, MessageType.ride_cancelled)


def test_ws_reconnect(client, profile_factory, make_token_headers):
    receiver = profile_factory()
    with client as cli:
        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(receiver.user_id)) as ws:
            time.sleep(0.1)
            ws.receive_json()

        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(receiver.user_id)) as ws:
            time.sleep(0.1)
            ws.receive_json()
