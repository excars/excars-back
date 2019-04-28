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


def test_ws_close_for_unauthorized_user(client):
    with pytest.raises(WebSocketDisconnect):
        with client as cli, cli.websocket_connect("/api/v1/ws") as ws:
            data = ws.receive_json()
            assert data == {"type": MessageType.map, "data": []}


def test_ws_receive_empty_map(client, make_token_headers):
    with client as cli, cli.websocket_connect("/api/v1/ws", headers=make_token_headers()) as ws:
        data = ws.receive_json()
        assert data == {"type": MessageType.map, "data": []}


@pytest.mark.parametrize("role", [Role.driver, Role.hitchhiker])
def test_ws_receive_map_for_user_without_ride(client, location_factory, profile_factory, make_token_headers, role):
    sender = profile_factory(role=role, save=True)
    location = location_factory(user_id=sender.user_id, save=True)

    receiver = profile_factory(role=Role.opposite(role), save=True)
    location_factory(user_id=receiver.user_id, save=True)

    with client as cli:
        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(receiver.user_id)) as ws:
            assert_map_item(ws.receive_json(), sender.user_id, location, has_same_ride=False)


@pytest.mark.parametrize("role", [Role.driver, Role.hitchhiker])
def test_ws_receive_map_without_ride_and_profile(client, location_factory, profile_factory, make_token_headers, role):
    sender = profile_factory(role=role, save=True)
    location = location_factory(user_id=sender.user_id, save=True)

    receiver_user_id = sender.user_id + 1
    location_factory(user_id=receiver_user_id, save=True)

    with client as cli:
        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(receiver_user_id)) as ws:
            assert_map_item(ws.receive_json(), sender.user_id, location, has_same_ride=False)


def test_ws_receive_no_map_without_profile(client, faker, location_factory, make_token_headers):
    receiver_user_id = faker.pyint()
    location_factory(user_id=receiver_user_id, save=True)
    location_factory(save=True)

    with client as cli:
        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(receiver_user_id)) as ws:
            data = ws.receive_json()
            assert data == {"type": MessageType.map, "data": []}


@pytest.mark.parametrize("role", [Role.driver, Role.hitchhiker])
def test_ws_receive_map_within_same_ride(client, location_factory, profile_factory, make_token_headers, role):
    ride_request = RideRequest(
        sender=profile_factory(role=role, save=True),
        receiver=profile_factory(role=Role.opposite(role), save=True),
        status=RideRequestStatus.accepted,
    )
    location = location_factory(user_id=ride_request.sender.user_id, save=True)
    location_factory(user_id=ride_request.receiver.user_id, save=True)

    with client as cli:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(repositories.rides.update_request(cli.app.redis_cli, ride_request))

        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(ride_request.receiver.user_id)) as ws:
            assert_map_item(ws.receive_json(), ride_request.sender.user_id, location, has_same_ride=True)


@pytest.mark.parametrize("role", [Role.driver, Role.hitchhiker])
def test_ws_receive_map_within_different_ride(client, location_factory, profile_factory, make_token_headers, role):
    ride_request = RideRequest(
        sender=profile_factory(role=role, save=True),
        receiver=profile_factory(role=Role.opposite(role), save=True),
        status=RideRequestStatus.accepted,
    )
    location_factory(user_id=ride_request.receiver.user_id, save=True)

    receiver = profile_factory(role=role, save=True)
    location_factory(user_id=receiver.user_id, save=True)

    with client as cli:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(repositories.rides.update_request(cli.app.redis_cli, ride_request))

        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(receiver.user_id)) as ws:
            assert ws.receive_json() == {"type": MessageType.map, "data": []}


def test_ws_send_location(client, profile_factory, make_token_headers):
    sender = profile_factory(role=Role.driver, save=True)

    with client as cli:
        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(sender.user_id)) as ws:
            ws.send_json({"type": MessageType.location, "data": {"longitude": 1, "latitude": 1, "course": -1}})


def test_ws_send_invalid_data(client, profile_factory, make_token_headers):
    sender = profile_factory(role=Role.driver, save=True)

    with client as cli:
        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(sender.user_id)) as ws:
            ws.send_json({"type": MessageType.location, "data": {"longitude": 1}})
            message = ws.receive_json()
            assert message["type"] == MessageType.error
            assert isinstance(message["data"], list)


def test_ws_receive_ride_requested(client, profile_factory, make_token_headers):
    ride_request = RideRequest(
        sender=profile_factory(role=Role.driver, save=True),
        receiver=profile_factory(role=Role.hitchhiker, save=True),
        status=RideRequestStatus.requested,
    )

    with client as cli:
        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(ride_request.receiver.user_id)) as ws:
            loop = asyncio.get_event_loop()
            loop.create_task(repositories.stream.ride_requested(cli.app.redis_cli, ride_request))
            ws.receive_json()
            ws.receive_json()
            message = ws.receive_json()
            assert message["type"] == MessageType.ride_requested


@pytest.mark.parametrize(
    "status,expected",
    [
        (RideRequestStatus.accepted, MessageType.ride_request_accepted),
        (RideRequestStatus.declined, MessageType.ride_request_declined),
    ],
)
def test_ws_receive_ride_request_updated(client, profile_factory, make_token_headers, status, expected):
    ride_request = RideRequest(
        sender=profile_factory(role=Role.driver, save=True),
        receiver=profile_factory(role=Role.hitchhiker, save=True),
        status=status,
    )

    with client as cli:
        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(ride_request.sender.user_id)) as ws:
            loop = asyncio.get_event_loop()
            loop.create_task(repositories.stream.request_updated(cli.app.redis_cli, ride_request))
            ws.receive_json()
            ws.receive_json()
            message = ws.receive_json()
            assert message["type"] == expected


@pytest.mark.parametrize("role", [Role.driver, Role.hitchhiker])
def test_ws_ride_updated(client, profile_factory, make_token_headers, role):
    ride_request = RideRequest(
        sender=profile_factory(role=role, save=True),
        receiver=profile_factory(role=Role.opposite(role), save=True),
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
            ws.receive_json()
            ws.receive_json()
            assert ws.receive_json()["type"] == MessageType.ride_updated


def test_ws_ride_cancelled(client, profile_factory, make_token_headers):
    ride_request = RideRequest(
        sender=profile_factory(role=Role.driver, save=True),
        receiver=profile_factory(role=Role.hitchhiker, save=True),
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
            ws.receive_json()
            ws.receive_json()
            message = ws.receive_json()
            assert message["type"] == MessageType.ride_cancelled
