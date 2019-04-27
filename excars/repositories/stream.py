from aioredis import Redis

from excars.models.messages import Message, MessageType
from excars.models.rides import RideRequest


async def _produce(redis_cli: Redis, user_id: int, message: Message):
    await redis_cli.xadd(f"stream:{user_id}", fields={"message": message.json()})


async def ride_requested(redis_cli: Redis, ride_request: RideRequest):
    message = Message(type=MessageType.ride_requested, data=ride_request)
    await _produce(redis_cli, user_id=ride_request.receiver.user_id, message=message)
