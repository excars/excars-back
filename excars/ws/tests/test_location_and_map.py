import asyncio

import pytest


async def fake_coro():
    return


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_publish_location(test_cli, add_jwt, mocker):
    mocker.patch('excars.ws.consumers.init', lambda *args, **kwargs: fake_coro())
    url = await add_jwt('/stream')
    conn = await test_cli.ws_connect(url)
    await conn.send_json({'data': {'longitude': 1, 'latitude': 1, 'course': -1}, 'type': 'LOCATION'})

    with pytest.raises(asyncio.TimeoutError):
        await conn.receive_json(timeout=0.2)
