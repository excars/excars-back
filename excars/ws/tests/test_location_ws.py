import pytest


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_publish_location(test_cli, add_jwt):
    url = await add_jwt('/stream')
    conn = await test_cli.ws_connect(url)
    await conn.send_json({'data': {'longitude': 1, 'latitude': 1}, 'type': 'LOCATION'})
    locations = await conn.receive_json()
    assert locations == {'data': {}, 'type': 'MAP'}
