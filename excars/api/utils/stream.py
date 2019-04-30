import asyncio
from asyncio import Task

from aioredis import Redis
from pydantic import ValidationError
from starlette.websockets import WebSocket

from excars import config, repositories
from excars.models.messages import Message
from excars.models.user import User


def init(websocket: WebSocket, user: User, redis_cli: Redis) -> Task:
    return asyncio.create_task(init_stream(websocket, user, redis_cli))


async def init_stream(websocket: WebSocket, user: User, redis_cli: Redis):
    await repositories.stream.create(redis_cli, user_id=user.user_id)

    while True:
        messages = await repositories.stream.list_messages_for(redis_cli, user_id=user.user_id)
        for stream_message in messages:
            try:
                message = Message.parse_raw(stream_message.data[b"message"])
            except (KeyError, ValidationError):
                continue
            await websocket.send_text(message.json())
            await repositories.stream.ack(redis_cli, user_id=user.user_id, message_id=stream_message.message_id)
        await asyncio.sleep(config.READ_STREAM_FREQUENCY)
