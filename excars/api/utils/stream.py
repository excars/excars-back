import asyncio

from aioredis import Redis
from pydantic import ValidationError
from starlette.websockets import WebSocket, WebSocketState

from excars import config, repositories
from excars.models.messages import Message
from excars.models.user import User


async def init(websocket: WebSocket, user: User, redis_cli: Redis) -> None:
    await repositories.stream.create(redis_cli, user_id=user.user_id)
    while websocket.application_state == WebSocketState.CONNECTED:
        messages = await repositories.stream.list_messages_for(redis_cli, user_id=user.user_id)
        for stream_message in messages:
            try:
                message = Message.parse_raw(stream_message.data[b"message"])
            except (KeyError, ValidationError):
                continue
            await websocket.send_text(message.json())
            await repositories.stream.ack(redis_cli, user_id=user.user_id, message_id=stream_message.message_id)
        await asyncio.sleep(config.READ_STREAM_FREQUENCY)
