import asyncio

import sanic_jwt
from sanic import Blueprint

import ujson

from . import event, utils

bp = Blueprint('ws_location')

event.discover()


@bp.websocket('/stream')
@sanic_jwt.inject_user()
@sanic_jwt.protected()
async def channel(request, ws, user):
    await asyncio.gather(
        listeners(request, ws, user),
        _stream_events(request, ws, user),
        *_publishers(request, ws, user),
    )


async def listeners(request, ws, user):
    while True:
        try:
            message = ujson.loads(await ws.recv())
        except ValueError:
            continue
        handler = event.get_listener(message['type'])
        if handler:
            await handler(request, message['data'], user)


async def _stream_events(request, ws, user):
    redis = request.app.redis
    user_uid = str(user.uid)
    stream = utils.get_user_stream(user_uid)

    # push message to stream just to create it
    await redis.xadd(
        stream=stream,
        fields={b'type': b'USER_CONNECT', b'user': user_uid}
    )

    await redis.xgroup_create(
        stream=stream,
        group_name=user_uid,
    )

    while True:
        await asyncio.sleep(0.1)
        messages = await redis.xread_group(
            group_name=user_uid,
            consumer_name=user_uid,
            streams=[stream],
            latest_ids=['>'],
            timeout=1,
        )
        for message in messages:
            message = message[2]
            handler = event.get_stream_message_handler(message.pop(b'type', b'').decode())
            if handler:
                await handler(request, ws, message, user)


def _publishers(request, ws, user):
    return [publisher(request, ws, user) for publisher in event.get_publishers()]
