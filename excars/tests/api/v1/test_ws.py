# pylint: disable=too-many-locals,too-many-statements,

import asyncio

import pytest

from excars import repositories
from excars.models.locations import Location, MapItem
from excars.models.messages import MessageType
from excars.models.profiles import Role
from excars.models.rides import RideRequest, RideRequestStatus


def test_ws_receive_empty_map(client, make_token_headers):
    with client as cli, cli.websocket_connect("/api/v1/ws", headers=make_token_headers()) as ws:
        data = ws.receive_json()
        assert data == {"type": MessageType.map, "data": []}


@pytest.mark.parametrize("role", [Role.driver, Role.hitchhiker])
def test_ws_send_map_for_user_without_ride(client, faker, profile_factory, make_token_headers, role):
    latitude = float(faker.latitude())
    longitude = float(faker.longitude())
    profile1 = profile_factory(role=role)
    profile2 = profile_factory(role=Role.opposite(role))
    location1 = Location(latitude=latitude, longitude=longitude, course=faker.coordinate())
    location2 = Location(latitude=latitude + 0.1, longitude=longitude + 0.1, course=faker.coordinate())

    with client as cli:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(repositories.profile.save(cli.app.redis_cli, profile1))
        loop.run_until_complete(repositories.profile.save(cli.app.redis_cli, profile2))
        loop.run_until_complete(repositories.locations.save_for(cli.app.redis_cli, profile1.user_id, location1))
        loop.run_until_complete(repositories.locations.save_for(cli.app.redis_cli, profile2.user_id, location2))

        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(profile2.user_id)) as ws:
            message = ws.receive_json()
            assert message["type"] == MessageType.map
            map_item = MapItem(**message["data"][0])
            assert map_item.user_id == profile1.user_id
            assert map_item.location.user_id == profile1.user_id
            assert map_item.location.latitude == location1.latitude
            assert map_item.location.longitude == location1.longitude
            assert map_item.has_same_ride is False


@pytest.mark.parametrize("role", [Role.driver, Role.hitchhiker])
def test_ws_send_map_for_user_without_ride_and_profile(client, faker, profile_factory, make_token_headers, role):
    latitude = float(faker.latitude())
    longitude = float(faker.longitude())
    profile1 = profile_factory(role=role)
    location1 = Location(latitude=latitude, longitude=longitude, course=faker.coordinate())
    location2 = Location(latitude=latitude + 0.1, longitude=longitude + 0.1, course=faker.coordinate())
    curr_user_id = faker.pyint()

    with client as cli:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(repositories.profile.save(cli.app.redis_cli, profile1))
        loop.run_until_complete(repositories.locations.save_for(cli.app.redis_cli, profile1.user_id, location1))
        loop.run_until_complete(repositories.locations.save_for(cli.app.redis_cli, curr_user_id, location2))

        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(curr_user_id)) as ws:
            data = ws.receive_json()
            assert data["type"] == MessageType.map
            map_item = MapItem(**data["data"][0])
            assert map_item.user_id == profile1.user_id
            assert map_item.location.user_id == profile1.user_id
            assert map_item.location.latitude == location1.latitude
            assert map_item.location.longitude == location1.longitude
            assert map_item.has_same_ride is False


def test_ws_send_map_filter_location_without_profile(client, faker, make_token_headers):
    latitude = float(faker.latitude())
    longitude = float(faker.longitude())
    location1 = Location(latitude=latitude, longitude=longitude, course=faker.coordinate())
    location2 = Location(latitude=latitude + 0.1, longitude=longitude + 0.1, course=faker.coordinate())
    curr_user_id = faker.pyint()

    with client as cli:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(repositories.locations.save_for(cli.app.redis_cli, faker.pyint(), location1))
        loop.run_until_complete(repositories.locations.save_for(cli.app.redis_cli, curr_user_id, location2))

        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(curr_user_id)) as ws:
            data = ws.receive_json()
            assert data == {"type": MessageType.map, "data": []}


@pytest.mark.parametrize("role", [Role.driver, Role.hitchhiker])
def test_ws_send_map_within_same_ride(client, faker, profile_factory, make_token_headers, role):
    latitude = float(faker.latitude())
    longitude = float(faker.longitude())
    profile1 = profile_factory(role=role)
    profile2 = profile_factory(role=Role.opposite(role))
    location1 = Location(latitude=latitude, longitude=longitude, course=faker.coordinate())
    location2 = Location(latitude=latitude + 0.1, longitude=longitude + 0.1, course=faker.coordinate())
    ride_request = RideRequest(sender=profile1, receiver=profile2, status=RideRequestStatus.accepted)

    with client as cli:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(repositories.profile.save(cli.app.redis_cli, profile1))
        loop.run_until_complete(repositories.profile.save(cli.app.redis_cli, profile2))
        loop.run_until_complete(repositories.locations.save_for(cli.app.redis_cli, profile1.user_id, location1))
        loop.run_until_complete(repositories.locations.save_for(cli.app.redis_cli, profile2.user_id, location2))
        loop.run_until_complete(repositories.rides.update_request(cli.app.redis_cli, ride_request))
        with cli.websocket_connect("/api/v1/ws", headers=make_token_headers(profile2.user_id)) as ws:
            message = ws.receive_json()
            assert message["type"] == MessageType.map
            map_item = MapItem(**message["data"][0])
            assert map_item.user_id == profile1.user_id
            assert map_item.location.user_id == profile1.user_id
            assert map_item.location.latitude == location1.latitude
            assert map_item.location.longitude == location1.longitude
            assert map_item.has_same_ride is True
