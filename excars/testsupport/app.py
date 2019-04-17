# pylint: disable=redefined-outer-name

import asyncio

import pytest
from sanic import websocket

from excars.app import create_app


@pytest.yield_fixture(scope="session")
def loop():
    _loop = asyncio.get_event_loop_policy().new_event_loop()
    yield _loop
    _loop.close()


@pytest.yield_fixture
def app():
    yield create_app()


@pytest.fixture
def test_cli(loop, app, test_client, mocker):
    mocker.patch("excars.settings.PUBLISH_MAP_FREQUENCY", 0.1)
    mocker.patch("excars.settings.READ_STREAM_FREQUENCY", 0.1)
    mocker.patch("excars.settings.USER_DATA_TTL_ON_CLOSE", 0.1)
    return loop.run_until_complete(test_client(app, protocol=websocket.WebSocketProtocol))
