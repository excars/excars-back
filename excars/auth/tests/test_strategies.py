# pylint: disable=redefined-outer-name

from unittest import mock

import pytest
from social_core.backends.google import GoogleOAuth2

from excars.auth import strategies


@pytest.fixture
def request_mock():
    request = mock.MagicMock(
        get=mock.MagicMock(return_value={
            'code': '1234'
        })
    )
    request.app.config.APP_NAME = 'excars'

    request.form = {'post': 'data'}
    request.args = {'query': 'param'}

    request.host = 'localhost:8080'
    request.path = '/posts/1/'
    request.scheme = 'https'

    return request


@pytest.fixture
def storage_mock():
    return mock.MagicMock()


@pytest.fixture
def strategy(storage_mock, request_mock):
    return strategies.SanicStrategy(storage_mock, request=request_mock)


def test_load_strategy(request_mock):
    assert isinstance(strategies.load_strategy(request_mock), strategies.SanicStrategy)


def test_load_backend(strategy):
    assert isinstance(strategies.load_backend(strategy), GoogleOAuth2)


def test_get_settings(strategy):
    assert strategy.get_setting('APP_NAME') == 'excars'


def test_request_data(strategy):
    assert strategy.request_data() == {'code': '1234'}


def test_request_post(strategy):
    assert strategy.request_post() == {'post': 'data'}


def test_request_get(strategy):
    assert strategy.request_get() == {'query': 'param'}


def test_request_host(strategy):
    assert strategy.request_host() == 'localhost'


def test_request_port(strategy):
    assert strategy.request_port() == '8080'


def test_request_path(strategy):
    assert strategy.request_path() == '/posts/1/'


def test_request_is_secure(strategy):
    assert strategy.request_is_secure() is True


@pytest.mark.parametrize(['path', 'expected'], [
    (None, 'https://localhost:8080/posts/1/'),
    ('/my/path', 'https://localhost:8080/my/path')
])
def test_build_absolute_uri(strategy, path, expected):
    assert strategy.build_absolute_uri(path) == expected


def test_redirect(strategy):
    with mock.patch('sanic.response.redirect') as redirect_mock:
        strategy.redirect('/')

    redirect_mock.assert_called_once_with('/')


def test_html(strategy):
    with mock.patch('sanic.response.html') as html_mock:
        strategy.html('content')

    html_mock.assert_called_once_with('content')


def test_session_get(strategy):
    assert strategy.session_get('key') is None


def test_session_set(strategy):
    assert strategy.session_set('key', 'value') is None


def test_session_pop(strategy):
    assert strategy.session_pop('key') is None
