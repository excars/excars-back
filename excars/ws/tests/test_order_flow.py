import asyncio

import pytest

import ujson
from excars.ws import event, utils


@pytest.fixture
def ping_event():

    @event.stream_handler('PING')
    async def handler(request, ws, message, user):
        del request, message, user
        await ws.send(ujson.dumps({'type': 'PONG', 'connected': True}))

    return None


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_simple_stream_connect(test_cli, add_jwt):
    url = await add_jwt('/stream')
    conn = await test_cli.ws_connect(url)

    with pytest.raises(asyncio.TimeoutError):
        await conn.receive_json(timeout=0.2)


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_group_recreate_stream_connect(test_cli, add_jwt, create_user, ping_event):
    del ping_event

    user = create_user(uid='a12d909f-81bb-408e-a337-b2d1b761c031')
    url = await add_jwt('/stream', user_id=user.id)
    stream = utils.get_user_stream(str(user.uid))
    conn = await test_cli.ws_connect(url)

    # This is some kind of a hack: ws_connect seems to be lazy, so we open connection like this
    try:
        await conn.receive_json(timeout=0.1)
    except asyncio.TimeoutError:
        pass

    await test_cli.app.redis.xadd(
        stream=stream,
        fields={
            b'type': b'PING',
        }
    )

    response = await conn.receive_json(timeout=0.2)

    assert response == {
        'type': 'PONG',
        'connected': True,
    }


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_group_recreate_stream_connect_twice(test_cli, add_jwt, create_user, ping_event):
    user = create_user(uid='a12d909f-81bb-408e-a337-b2d1b761c031')
    url = await add_jwt('/stream', user_id=user.id)
    stream = utils.get_user_stream(str(user.uid))

    # Run test two times to simulate initial and second connections of the client
    for i in range(2):
        conn = await test_cli.ws_connect(url)

        try:
            await conn.receive_json(timeout=0.1)
        except asyncio.TimeoutError:
            pass

        await test_cli.app.redis.xadd(
            stream=stream,
            fields={
                b'type': b'PING',
            }
        )

        check = await conn.receive_json(timeout=0.1)

        assert check == {
            'type': 'PONG',
            'connected': True,
        }

        conn.close()
