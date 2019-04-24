# pylint: disable=redefined-outer-name
import random

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


@pytest.fixture
def client(mocker):
    import asyncio

    from starlette.testclient import TestClient, WebSocketTestSession

    from excars.main import app

    class WebSocketTestSessionMonkeyPatch(WebSocketTestSession):
        __loop = asyncio.get_event_loop()

        @property
        def _loop(self):
            return self.__loop

        @_loop.setter
        def _loop(self, value):  # pylint: disable=no-self-use
            value.stop()
            value.close()

    mocker.patch("starlette.testclient.WebSocketTestSession", WebSocketTestSessionMonkeyPatch)

    yield TestClient(app)

    with TestClient(app) as cli:
        asyncio.get_event_loop().run_until_complete(cli.app.redis_cli.flushdb())


@pytest.fixture
def profile_factory(faker):
    def profile(**kwargs):
        from excars.models.profiles import Profile, Role

        defaults = {
            "user_id": faker.pyint(),
            "name": faker.name(),
            "avatar": faker.url(),
            "role": random.choice([Role.driver, Role.hitchhiker]),
            "destination": {"name": faker.name(), "latitude": faker.latitude(), "longitude": faker.longitude()},
        }
        defaults.update(kwargs)
        return Profile(**defaults)

    return profile
