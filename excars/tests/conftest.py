# pylint: disable=redefined-outer-name

import asyncio
import random
from typing import Optional

import pytest


@pytest.fixture
def make_token_payload(faker):
    def token_payload(**kwargs):
        defaults = {
            "sub": faker.pyint(),
            "iss": "https://accounts.google.com",
            "email": faker.email(),
            "name": faker.name(),
            "picture": faker.url(),
            "given_name": faker.first_name(),
            "family_name": faker.last_name(),
        }
        defaults.update(kwargs)
        return defaults

    return token_payload


@pytest.fixture
def make_token_headers(mocker, faker, make_token_payload):
    def token_headers_for(user_id: int = None):
        user_id = user_id or faker.pyint()
        payload = make_token_payload(sub=user_id)
        mocker.patch("excars.api.utils.security.verify_oauth2_token", return_value=payload)
        return {"Authorization": "Bearer fake.jwt.token"}

    return token_headers_for


@pytest.yield_fixture
def client(mocker):
    from starlette.testclient import TestClient, WebSocketTestSession
    from starlette.types import Message

    from excars.main import app

    # See https://github.com/encode/starlette/issues/487
    class WebSocketTestSessionMonkeyPatch(WebSocketTestSession):
        __loop = asyncio.get_event_loop()

        @property
        def _loop(self):
            return self.__loop

        @_loop.setter
        def _loop(self, value):  # pylint: disable=no-self-use
            value.stop()
            value.close()

        # See https://github.com/encode/starlette/pull/459
        async def _asgi_receive(self) -> Message:
            while self._receive_queue.empty():
                await asyncio.sleep(0)
            return self._receive_queue.get()

    mocker.patch("starlette.testclient.WebSocketTestSession", WebSocketTestSessionMonkeyPatch)

    try:
        yield TestClient(app)
    finally:
        with TestClient(app) as cli:
            asyncio.get_event_loop().run_until_complete(cli.app.redis_cli.flushdb())


@pytest.fixture
def profile_factory(client, faker):
    def make_profile(**kwargs):
        from excars.models.profiles import Profile, Role

        defaults = {
            "user_id": faker.pyint(),
            "name": faker.name(),
            "avatar": faker.url(),
            "role": random.choice([Role.driver, Role.hitchhiker]),
            "destination": {"name": faker.name(), "latitude": faker.latitude(), "longitude": faker.longitude()},
        }
        defaults.update(kwargs)
        profile = Profile(**defaults)

        from excars import repositories

        loop = asyncio.get_event_loop()
        with client as cli:
            loop.run_until_complete(repositories.profile.save(cli.app.redis_cli, profile))

        return profile

    return make_profile


@pytest.fixture
def location_factory(client, faker):
    latitude = float(faker.coordinate(center=50))  # latitude should be in -85..+85
    longitude = float(faker.longitude())

    def make_location(*, user_id: Optional[str] = None):
        from excars.models.locations import Location

        location = Location(latitude=latitude + 0.1, longitude=longitude + 0.1, course=faker.coordinate())

        loop = asyncio.get_event_loop()
        user_id = user_id or faker.pyint()
        with client as cli:
            from excars import repositories

            loop.run_until_complete(repositories.locations.save_for(cli.app.redis_cli, user_id, location))

        return location

    return make_location
