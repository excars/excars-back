import pytest

from excars.auth import models


@pytest.fixture
def create_user():
    return lambda **kwargs: models.User.create(
        **{
            'username': 'excars',
            'email': 'excars@gmail.com',
            **kwargs,
        }
    )


@pytest.fixture
def add_jwt(request, test_cli):
    async def wrapper(url, user_id=None):
        if user_id is None:
            user_id = request.getfixturevalue('create_user')(username='first').id
        jwt_token = await test_cli.app.auth.generate_access_token({'user_id': user_id})
        return f'{url}?access_token={jwt_token}'
    return wrapper
