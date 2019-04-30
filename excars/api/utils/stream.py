import asyncio
from asyncio import Task

from aioredis import Redis
from starlette.websockets import WebSocket

from excars import config
from excars.models.messages import Message
from excars.models.user import User


def init(websocket: WebSocket, user: User, redis_cli: Redis) -> Task:
    return asyncio.create_task(init_stream(websocket, user, redis_cli))


async def init_stream(websocket: WebSocket, user: User, redis_cli: Redis):
    stream = f"stream:{user.user_id}"

    # push message to stream just to create it
    await redis_cli.xadd(stream=stream, fields={b"type": b"CREATE", b"user": user.user_id})

    groups = [group[b"name"].decode() for group in await redis_cli.xinfo_groups(stream)]
    if user.user_id not in groups:
        await redis_cli.xgroup_create(stream=stream, group_name=user.user_id)

    while True:
        messages = await redis_cli.xread_group(
            group_name=user.user_id, consumer_name=user.user_id, streams=[stream], latest_ids=[">"], timeout=1
        )
        for stream_message in messages:
            message = Message.parse_raw(stream_message[2][b"message"])
            await websocket.send_text(message.json())
        await asyncio.sleep(config.READ_STREAM_FREQUENCY)
