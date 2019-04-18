# pylint: disable=redefined-outer-name
import random

import pytest
from starlette.testclient import TestClient

from excars.main import app


@pytest.fixture
def token_payload():
    return {
        "sub": "101248120531028200825",
        "iss": "https://accounts.google.com",
        "email": "example@gmail.com",
        "name": "Name Placeholder",
        "picture": "path/to/photo.jpg",
        "given_name": "Name",
        "family_name": "Placeholder",
    }


@pytest.fixture
def token_headers(mocker, token_payload):
    with mocker.patch("excars.api.utils.security.verify_oauth2_token", return_value=token_payload):
        yield {"Authorization": "Bearer fake.jwt.token"}


@pytest.fixture
def client():
    return TestClient(app)


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
