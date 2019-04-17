import random
import string

import pytest

from excars.auth import models


@pytest.fixture
def create_user():
    def _create_user(**kwargs):
        if "username" in kwargs:
            name = kwargs["username"]
        else:
            name = list(string.ascii_lowercase)
            random.shuffle(name)
            name = "".join(name[: random.randint(5, len(name))]).capitalize()
        return models.User.create(**{"username": name, "email": f"{name}@gmail.com", **kwargs})

    return _create_user


@pytest.fixture
def add_jwt(request, test_cli):
    async def wrapper(url, user_uid=None):
        if user_uid is None:
            user_uid = request.getfixturevalue("create_user")(username="first").uid
        jwt_token = await test_cli.app.auth.generate_access_token({"user_id": str(user_uid)})
        return f"{url}?access_token={jwt_token}"

    return wrapper
