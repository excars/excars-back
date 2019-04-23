from aioredis import Redis

from excars import repositories
from excars.models.locations import Location
from excars.models.messages import Message, MessageType
from excars.models.user import User


async def handle(message: Message, user: User, redis_cli: Redis):
    if message.type == MessageType.location:
        await receive_location(Location(**message.data), user, redis_cli)


async def receive_location(location: Location, user: User, redis_cli: Redis):
    await repositories.locations.save_for(redis_cli, user.user_id, location)
