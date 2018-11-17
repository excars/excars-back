import pytest


@pytest.mark.require_redis
async def test_publish_location(test_cli):
    conn = await test_cli.ws_connect('/stream')
    await conn.send_json({'data': {'longitude': 1, 'latitude': 1}, 'type': 'LOCATION'})
    locations = await conn.receive_json()
    assert locations == {'data': {}, 'type': 'MAP'}
