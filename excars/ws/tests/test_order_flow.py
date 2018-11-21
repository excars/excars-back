
import pytest


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_stream_connect(test_cli, add_jwt):
    url = await add_jwt('/stream')
    conn = await test_cli.ws_connect(url)
    check = await conn.receive_json()
    assert check == {'connected': True, 'type': 'CHECK'}
