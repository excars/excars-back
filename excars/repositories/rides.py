import asyncio
from typing import Optional

from aioredis import Redis

from excars import config
from excars.models.profiles import Profile, Role
from excars.models.rides import Passenger, Ride, RideRequest

from . import profile as profile_repo


async def create_request(redis_cli: Redis, ride_request: RideRequest) -> None:
    await redis_cli.setex(
        f"ride:{ride_request.ride_uid}:request:{ride_request.passenger.user_id}",
        value=ride_request.status.value,
        seconds=config.RIDE_REQUEST_TTL,
    )


async def update_request(redis_cli: Redis, ride_request: RideRequest) -> None:
    ride_key = f"ride:{ride_request.ride_uid}"
    await redis_cli.delete(f"{ride_key}:request:{ride_request.passenger.user_id}")
    await redis_cli.set(
        f"{ride_key}:passenger:{ride_request.passenger.user_id}",
        value=ride_request.status.value,
        expire=config.RIDE_TTL,
    )


async def request_exists(redis_cli: Redis, ride_request: RideRequest) -> bool:
    return bool(await redis_cli.exists(f"ride:{ride_request.ride_uid}:request:{ride_request.passenger.user_id}"))


async def delete_or_exclude(redis_cli: Redis, profile: Profile, timeout: int = 0) -> None:
    if profile.role == Role.hitchhiker:
        await _exclude(redis_cli, profile.user_id, timeout)
    elif profile.role == Role.driver:
        await _delete(redis_cli, profile.user_id, timeout)


async def _delete(redis_cli: Redis, ride_id: int, timeout: int) -> None:
    ride = await get(redis_cli, ride_id)
    keys = [f"ride:{ride_id}:passenger:{passenger.profile.user_id}" for passenger in ride.passengers]
    await asyncio.gather(*[redis_cli.expire(key, timeout) for key in keys])


async def _exclude(redis_cli: Redis, user_id: int, timeout: int) -> None:
    ride_id = await get_ride_id(redis_cli, user_id)
    if ride_id:
        await redis_cli.expire(f"ride:{ride_id}:passenger:{user_id}", timeout)


async def get(redis_cli: Redis, ride_id: int) -> Ride:
    keys = [key async for key in redis_cli.iscan(match=f"ride:{ride_id}:passenger:*")]
    passengers_key = [key.decode().rpartition(":")[-1] for key in keys]

    driver = await profile_repo.get(redis_cli, ride_id)

    passengers = []
    for key in passengers_key:
        passengers.append(
            Passenger(
                profile=await profile_repo.get(redis_cli, key),
                status=(await redis_cli.get(f"ride:{ride_id}:passenger:{key}")).decode(),
            )
        )

    return Ride(ride_id=str(ride_id), driver=driver, passengers=passengers)


async def get_ride_id(redis_cli: Redis, user_id: int) -> Optional[int]:
    async for key in redis_cli.iscan(match=f"ride:*:passenger:{user_id}"):
        return int(key.decode().split(":")[1])

    async for _ in redis_cli.iscan(match=f"ride:{user_id}:passenger:*"):  # noqa
        return int(user_id)

    return None


async def persist(redis_cli: Redis, user_id: int) -> None:
    ride_id = await get_ride_id(redis_cli, user_id)
    keys = [key async for key in redis_cli.iscan(match=f"ride:{ride_id}:passenger:*")]
    await asyncio.gather(*[redis_cli.persist(key) for key in keys])
