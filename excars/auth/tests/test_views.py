# pylint: disable=redefined-outer-name

from unittest import mock

import pytest
from sanic_jwt import exceptions

from excars.auth import models, views


@pytest.fixture
def request_mock(loop):
    request = mock.MagicMock()
    request.json = {
        'code': '1234',
        'redirect_uri': 'http://localhost:3000'
    }
    request.app.loop = loop

    request.scheme = 'https'
    request.host = 'localhost:8080'
    request.path = '/posts/1/'

    request.app.config.SOCIAL_AUTH_ALLOWED_EMAIL_DOMAINS = ['excars.com']

    return request


async def test_authenticate_success(request_mock):
    strategy = mock.MagicMock()
    backend = mock.MagicMock()
    backend.complete = mock.MagicMock(
        return_value=models.User(id=1, username='user', email='user@excars.com')
    )

    load_strategy = mock.patch('excars.auth.strategies.load_strategy', return_value=strategy)
    load_backend = mock.patch('excars.auth.strategies.load_backend', return_value=backend)

    with load_strategy as load_strategy_mock, load_backend as load_backend_mock:
        response = await views.authenticate(request_mock)

    assert response == {'user_id': 1}

    assert load_strategy_mock.call_count == 1
    assert load_strategy_mock.call_args == mock.call(request_mock)

    assert load_backend_mock.call_count == 1
    assert load_backend_mock.call_args == mock.call(strategy)

    assert backend.REDIRECT_STATE is False
    assert backend.STATE_PARAMETER is False
    assert backend.redirect_uri == 'http://localhost:3000'
    assert backend.complete.called


async def test_authenticate_failure_due_to_email_domain_restriction(request_mock):
    strategy = mock.MagicMock()
    backend = mock.MagicMock()
    backend.complete = mock.MagicMock(
        return_value=models.User(id=1, username='user', email='user@google.com')
    )

    load_strategy = mock.patch('excars.auth.strategies.load_strategy', return_value=strategy)
    load_backend = mock.patch('excars.auth.strategies.load_backend', return_value=backend)

    with load_strategy, load_backend:
        with pytest.raises(exceptions.AuthenticationFailed):
            await views.authenticate(request_mock)


@pytest.fixture
def user():
    return models.User.create(id=1, username='user', email='user@excars.com')


@pytest.mark.require_db
async def test_retrieve_user_returns_user(request_mock, user):
    payload = {'user_id': 1}

    response = await views.retrieve_user(request_mock, payload)

    assert response == {
        'id': user.id,
        'username': user.username,
        'email': user.email,
    }


@pytest.mark.require_db
@pytest.mark.parametrize('payload', [
    None,
    {},
    {'code': 1},
    {'user_id': 1},
])
async def test_retrieve_user_returns_none(request_mock, payload):
    response = await views.retrieve_user(request_mock, payload)
    assert response is None
