from aioredis import Redis

from excars import config
from excars.models.rides import RideRequest


async def create_request(redis_cli: Redis, ride_request: RideRequest):
    await redis_cli.setex(
        f"ride:{ride_request.ride_uid}:request:{ride_request.passenger.user_id}",
        value=ride_request.status.value,
        seconds=config.RIDE_REQUEST_TTL,
    )
