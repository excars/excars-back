
import pytest

from sanic.websocket import WebSocketProtocol
from excars.app import app


@pytest.fixture
def test_cli(loop, test_client):
    return loop.run_until_complete(test_client(app, protocol=WebSocketProtocol))


async def test_publish_location(test_cli):
    conn = await test_cli.ws_connect('/location')
    await conn.send_json({'longitude': 1, 'latitude': 1})
    print(await conn.receive_json())