import pytest
from sanic.websocket import WebSocketProtocol

from excars.app import app


@pytest.fixture
def test_cli(loop, test_client):
    return loop.run_until_complete(test_client(app, protocol=WebSocketProtocol))


@pytest.fixture(scope='function', autouse=True)
async def setup(loop, test_cli):
    await test_cli.app.redis.flushdb()
    yield
    await test_cli.app.redis.flushdb()


async def test_publish_location(test_cli):
    conn = await test_cli.ws_connect('/stream')
    await conn.send_json({'data': {'longitude': 1, 'latitude': 1}, 'type': 'LOCATION'})
    locations = await conn.receive_json()
    assert locations == {'data': {}, 'type': 'MAP'}
