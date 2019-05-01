from aioredis import Redis
from pydantic import ValidationError
from starlette.websockets import WebSocket

from excars import repositories
from excars.models.locations import Location
from excars.models.messages import Message, MessageType
from excars.models.user import User


async def init(websocket: WebSocket, user: User, redis_cli: Redis) -> None:
    while True:
        data = await websocket.receive_json()
        try:
            message = Message(**data)
            await handle(message, user, redis_cli)
        except ValidationError as exc:
            await websocket.send_text(Message(type=MessageType.error, data=exc.errors()).json())


async def handle(message: Message, user: User, redis_cli: Redis):
    if message.type == MessageType.location:
        await receive_location(Location(**message.data), user, redis_cli)


async def receive_location(location: Location, user: User, redis_cli: Redis) -> None:
    await repositories.locations.save_for(redis_cli, user.user_id, location)
