import asyncio

import pytest


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_simple_stream_connect(test_cli, add_jwt):
    url = await add_jwt('/stream')
    conn = await test_cli.ws_connect(url)
    try:
        await conn.receive_json(timeout=1)
    except asyncio.TimeoutError:
        assert True
    else:
        assert False


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_group_recreate_stream_connect(test_cli, add_jwt):
    url = await add_jwt('/stream')
    conn = await test_cli.ws_connect(url)

    await test_cli.ws_connect(url)
    check = await conn.receive_json()
    assert check == {'connected': True, 'type': 'CHECK'}
