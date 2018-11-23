import asyncio

import pytest

import ujson
from excars.ws import event, utils


@pytest.fixture
def listener_event():

    @event.listen('PING')
    async def handler(request, ws, message, user):
        del request, message, user
        await ws.send(ujson.dumps({
            'type': 'PONG',
            'connected': True,
        }))

    yield

    del event._listeners_registry['PING']

    return None


@pytest.fixture
def publisher_event():

    @event.publisher
    async def handler(request, ws, user):
        del request, user
        await ws.send(ujson.dumps({
            'type': 'PONG'
        }))

    yield

    event._publishers_registry = event._publishers_registry[:-1]

    return None


@pytest.fixture
def consumer_event():

    @event.consume('XPING')
    async def handler(request, ws, message, user):
        del request, message, user
        await ws.send(ujson.dumps({
            'type': 'XPONG',
            'connected': True,
        }))

    yield

    del event._consumers_registry['XPING']

    return None


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_stream_smoke(test_cli, add_jwt):
    url = await add_jwt('/stream')
    conn = await test_cli.ws_connect(url)

    with pytest.raises(asyncio.TimeoutError):
        await conn.receive_json(timeout=0.2)


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_reconnect_to_stream(test_cli, add_jwt):
    url = await add_jwt('/stream')

    for i in range(2):
        conn = await test_cli.ws_connect(url)

        with pytest.raises(asyncio.TimeoutError):
            await conn.receive_json(timeout=0.1)

        conn.close()


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_stream_listeners(test_cli, add_jwt, listener_event):
    del listener_event

    url = await add_jwt('/stream')
    conn = await test_cli.ws_connect(url)

    await conn.send_json({
        'type': 'PING',
        'data': {}
    })

    response = await conn.receive_json()

    assert response == {
        'type': 'PONG',
        'connected': True,
    }


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_stream_publishers(test_cli, add_jwt, publisher_event):
    del publisher_event

    url = await add_jwt('/stream')
    conn = await test_cli.ws_connect(url)

    response = await conn.receive_json()

    assert response == {
        'type': 'PONG',
    }


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_stream_consumer(test_cli, add_jwt, create_user, consumer_event):
    del consumer_event

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
            b'type': b'XPING',
        }
    )

    response = await conn.receive_json(timeout=0.2)

    assert response == {
        'type': 'XPONG',
        'connected': True,
    }
