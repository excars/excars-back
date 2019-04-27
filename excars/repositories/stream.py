from aioredis import Redis

from excars.models.messages import Message, MessageType
from excars.models.rides import RideRequest, RideRequestStatus


async def _produce(redis_cli: Redis, user_id: int, message: Message):
    await redis_cli.xadd(f"stream:{user_id}", fields={"message": message.json()})


async def ride_requested(redis_cli: Redis, ride_request: RideRequest):
    message = Message(type=MessageType.ride_requested, data=ride_request)
    await _produce(redis_cli, user_id=ride_request.receiver.user_id, message=message)


async def request_updated(redis_cli: Redis, ride_request: RideRequest):
    event_map = {
        RideRequestStatus.accepted: MessageType.ride_request_accepted,
        RideRequestStatus.declined: MessageType.ride_request_declined,
    }
    message = Message(type=event_map[ride_request.status], data=ride_request)
    await _produce(redis_cli, user_id=ride_request.sender.user_id, message=message)
