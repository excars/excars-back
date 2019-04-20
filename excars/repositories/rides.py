from aioredis import Redis

from excars import config
from excars.models.rides import RideRequest


async def create_request(redis_cli: Redis, ride_request: RideRequest):
    await redis_cli.setex(
        f"ride:{ride_request.ride_uid}:request:{ride_request.passenger.user_id}",
        value=ride_request.status.value,
        seconds=config.RIDE_REQUEST_TTL,
    )


async def update_request(redis_cli: Redis, ride_request: RideRequest):
    ride_key = f"ride:{ride_request.ride_uid}"
    await redis_cli.delete(f"{ride_key}:request:{ride_request.passenger.user_id}")
    await redis_cli.set(
        f"{ride_key}:passenger:{ride_request.passenger.user_id}",
        value=ride_request.status.value,
        expire=config.RIDE_TTL,
    )


async def request_exists(redis_cli: Redis, ride_request: RideRequest) -> bool:
    return bool(await redis_cli.exists(f"ride:{ride_request.ride_uid}:request:{ride_request.passenger.user_id}"))
