import asyncio
from typing import List

from aioredis import Redis

from excars.models.messages import Message, MessageType, StreamMessage
from excars.models.rides import Ride, RideRequest, RideRequestStatus


async def _produce(redis_cli: Redis, user_id: str, message: Message) -> None:
    await redis_cli.xadd(f"stream:{user_id}", fields={"message": message.json()})


async def _broadcast(redis_cli: Redis, user_ids: List[str], message: Message) -> None:
    await asyncio.gather(*[_produce(redis_cli, user_id, message) for user_id in user_ids])


async def create(redis_cli: Redis, user_id: str) -> None:
    await redis_cli.xadd(stream=f"stream:{user_id}", fields={b"type": b"CREATE", b"data": user_id})
    groups = [group[b"name"].decode() for group in await redis_cli.xinfo_groups(f"stream:{user_id}")]
    if user_id not in groups:
        await redis_cli.xgroup_create(stream=f"stream:{user_id}", group_name=user_id)


async def list_messages_for(redis_cli: Redis, user_id: str) -> List[StreamMessage]:
    messages = await redis_cli.xread_group(
        group_name=user_id, consumer_name=user_id, streams=[f"stream:{user_id}"], latest_ids=[">"], timeout=1
    )
    return [StreamMessage(*message) for message in messages]


async def ack(redis_cli: Redis, user_id: str, message_id: int) -> None:
    await redis_cli.xack(f"stream:{user_id}", group_name=user_id, id=message_id)


async def ride_requested(redis_cli: Redis, ride_request: RideRequest) -> None:
    message = Message(type=MessageType.ride_requested, data=ride_request)
    await _produce(redis_cli, user_id=ride_request.receiver.user_id, message=message)


async def request_updated(redis_cli: Redis, ride_request: RideRequest) -> None:
    event_map = {
        RideRequestStatus.accepted: MessageType.ride_request_accepted,
        RideRequestStatus.declined: MessageType.ride_request_declined,
    }
    message = Message(type=event_map[ride_request.status], data=ride_request)
    await _produce(redis_cli, user_id=ride_request.sender.user_id, message=message)


async def ride_updated(redis_cli: Redis, ride: Ride) -> None:
    user_ids = [passenger.profile.user_id for passenger in ride.passengers]
    user_ids.append(ride.driver.user_id)
    message = Message(type=MessageType.ride_updated, data=ride)
    await _broadcast(redis_cli, user_ids=user_ids, message=message)


async def ride_cancelled(redis_cli: Redis, ride: Ride) -> None:
    user_ids = [passenger.profile.user_id for passenger in ride.passengers]
    message = Message(type=MessageType.ride_cancelled, data=ride)
    await _broadcast(redis_cli, user_ids=user_ids, message=message)
