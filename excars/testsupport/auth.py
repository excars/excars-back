import pytest

from excars.auth import models


@pytest.fixture
def user():
    return models.User.create(
        id=1,
        username='excars',
        email='excars@gmail.com',
    )


@pytest.fixture
def add_jwt(request, test_cli):
    async def wrapper(url, user_id=None):
        if user_id is None:
            user_id = request.getfixturevalue('user').id
        jwt_token = await test_cli.app.auth.generate_access_token({'user_id': user_id})
        return f'{url}?access_token={jwt_token}'
    return wrapper
