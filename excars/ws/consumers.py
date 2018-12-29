import asyncio

from excars import redis as redis_utils

from . import event, utils


async def init(request, ws, user):
    redis = request.app.redis
    user_uid = str(user.uid)
    stream = utils.get_user_stream(user_uid)

    # push message to stream just to create it
    await redis.xadd(
        stream=stream,
        fields={
            b'type': b'CREATE',
            b'user': user_uid,
        }
    )

    groups = [group[b'name'].decode() for group in await redis.xinfo_groups(stream)]
    if user_uid not in groups:
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
            message = redis_utils.decode(message[2])
            handler = event.get_consumers(message.get('type', ''))
            if handler:
                await handler(request, ws, message, user)
