import asyncio
from typing import Optional

from aioredis import Redis

from excars import config
from excars.models.profiles import Profile, Role
from excars.models.rides import Passenger, Ride, RideRequest

from . import profile as profile_repo


def _get_ride_key(ride_id: str, passenger_id: str) -> str:
    return f"ride:{ride_id}:passenger:{passenger_id}"


def _get_ride_request_key(ride_id: str, passenger_id: str) -> str:
    return f"ride:{ride_id}:request:{passenger_id}"


async def create_request(redis_cli: Redis, ride_request: RideRequest) -> None:
    await redis_cli.setex(
        _get_ride_request_key(ride_request.ride_id, ride_request.passenger.user_id),
        value=ride_request.status.value,
        seconds=config.RIDE_REQUEST_TTL,
    )


async def update_request(redis_cli: Redis, ride_request: RideRequest) -> None:
    await redis_cli.delete(_get_ride_request_key(ride_request.ride_id, ride_request.passenger.user_id))
    await redis_cli.set(
        _get_ride_key(ride_request.ride_id, ride_request.passenger.user_id),
        value=ride_request.status.value,
        expire=config.RIDE_TTL,
    )


async def request_exists(redis_cli: Redis, ride_request: RideRequest) -> bool:
    return bool(await redis_cli.exists(_get_ride_request_key(ride_request.ride_id, ride_request.passenger.user_id)))


async def delete_or_exclude(redis_cli: Redis, profile: Profile, timeout: int = 0) -> None:
    if profile.role == Role.hitchhiker:
        await _exclude(redis_cli, profile.user_id, timeout)
    elif profile.role == Role.driver:
        await _delete(redis_cli, profile.user_id, timeout)


async def _delete(redis_cli: Redis, ride_id: str, timeout: int) -> None:
    ride = await get(redis_cli, ride_id)
    if ride is not None:
        keys = [_get_ride_key(ride_id, passenger.profile.user_id) for passenger in ride.passengers]
        await asyncio.gather(*[redis_cli.expire(key, timeout) for key in keys])


async def _exclude(redis_cli: Redis, user_id: str, timeout: int) -> None:
    ride_id = await get_ride_id(redis_cli, user_id)
    if ride_id:
        await redis_cli.expire(_get_ride_key(ride_id, user_id), timeout)


async def get(redis_cli: Redis, ride_id: str) -> Optional[Ride]:
    keys = [key async for key in redis_cli.iscan(match=_get_ride_key(ride_id, "*"))]
    if not keys:
        return None
    passengers_key = [key.decode().rpartition(":")[-1] for key in keys]

    driver = await profile_repo.get(redis_cli, ride_id)
    if driver is None:
        return None

    passengers = []
    for key in passengers_key:
        profile = await profile_repo.get(redis_cli, key)
        if profile is None:
            continue
        passengers.append(
            Passenger(profile=profile, status=(await redis_cli.get(_get_ride_key(ride_id, key))).decode())
        )
    if not passengers:
        return None

    return Ride(ride_id=ride_id, driver=driver, passengers=passengers)


async def get_ride_id(redis_cli: Redis, user_id: str) -> Optional[str]:
    async for key in redis_cli.iscan(match=_get_ride_key("*", user_id)):
        return str(key.decode().split(":")[1])

    async for _ in redis_cli.iscan(match=_get_ride_key(user_id, "*")):  # noqa
        return user_id

    return None


async def persist(redis_cli: Redis, user_id: str) -> None:
    ride_id = await get_ride_id(redis_cli, user_id)
    if ride_id is not None:
        keys = [key async for key in redis_cli.iscan(match=_get_ride_key(ride_id, "*"))]
        await asyncio.gather(*[redis_cli.persist(key) for key in keys])
