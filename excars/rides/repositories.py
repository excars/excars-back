import asyncio
import typing

from excars import redis as redis_utils
from excars import settings

from . import constants, entities, schemas


class ProfileRepository:

    def __init__(self, redis_cli):
        self.redis_cli = redis_cli

    @staticmethod
    def _get_key(uid):
        return f'user:{uid}'

    async def save(self, profile: entities.Profile):
        await self.redis_cli.hmset_dict(
            self._get_key(profile.uid),
            **schemas.ProfileRedisSchema().dump(profile).data,
        )

    async def get(self, user_uid: str) -> typing.Optional[entities.Profile]:
        payload = redis_utils.decode(await self.redis_cli.hgetall(self._get_key(user_uid)))

        data, errors = schemas.ProfileRedisSchema().load(payload)
        if errors:
            return None

        return data

    async def delete(self, user_uid: str):
        await self.redis_cli.delete(self._get_key(user_uid))

    async def expire(self, user_uid: str):
        await self.redis_cli.expire(
            self._get_key(user_uid),
            timeout=settings.USER_DATA_TTL_ON_CLOSE,
        )

    async def unexpire(self, user_uid: str):
        await self.redis_cli.persist(self._get_key(user_uid))


class RideRepository:

    REMOVE_KEY = 'remove:ride:{user_uid}'

    def __init__(self, redis_cli):
        self.redis_cli = redis_cli

    async def create_request(self, ride_request: entities.RideRequest):
        await self.redis_cli.setex(
            f'ride:{ride_request.ride_uid}:request:{ride_request.passenger.uid}',
            value=ride_request.status,
            seconds=settings.RIDE_REQUEST_TTL,
        )
        await StreamRepository(self.redis_cli).ride_requested(ride_request)

    async def update_request(self, ride_request: entities.RideRequest):
        ride_key = f'ride:{ride_request.ride_uid}'
        await self.redis_cli.delete(f'{ride_key}:request:{ride_request.passenger.uid}')

        status = ride_request.status
        await self.redis_cli.set(
            f'{ride_key}:passenger:{ride_request.passenger.uid}',
            value=status,
            expire=settings.RIDE_TTL,
        )

        stream_repo = StreamRepository(self.redis_cli)
        await stream_repo.request_updated(ride_request)

        ride = await self.get(ride_request.ride_uid)
        await stream_repo.ride_updated(ride)

    async def request_exists(self, ride_request: entities.RideRequest) -> bool:
        return bool(await self.redis_cli.exists(
            f'ride:{ride_request.ride_uid}:request:{ride_request.passenger.uid}'
        ))

    async def get(self, ride_uid: str) -> entities.Ride:
        keys = [key async for key in self.redis_cli.iscan(match=f'ride:{ride_uid}:passenger:*')]
        passengers_key = [key.decode().rpartition(':')[-1] for key in keys]

        profile_repo = ProfileRepository(self.redis_cli)
        driver = await profile_repo.get(ride_uid)

        passengers = []
        for key in passengers_key:
            passengers.append(entities.Passenger(
                profile=await profile_repo.get(key),
                status=await self.redis_cli.get(f'ride:{ride_uid}:passenger:{key}'),
            ))

        return entities.Ride(uid=str(ride_uid), driver=driver, passengers=passengers)

    async def delete(self, ride_uid: str) -> None:
        ride = await self.get(ride_uid)

        await StreamRepository(self.redis_cli).ride_cancelled(ride)

        keys = [f'ride:{ride_uid}:passenger:{passenger.profile.uid}' for passenger in ride.passengers]
        await asyncio.gather(*[self.redis_cli.delete(key) for key in keys])

    async def exclude(self, user_uid: str) -> None:
        ride_uid = await self.get_ride_uid(user_uid)
        if ride_uid:
            await self.redis_cli.delete(f'ride:{ride_uid}:passenger:{user_uid}')

            ride = await self.get(ride_uid)
            await StreamRepository(self.redis_cli).ride_updated(ride)

    async def get_ride_uid(self, user_uid: str) -> typing.Optional[str]:
        async for key in self.redis_cli.iscan(match=f'ride:*:passenger:{user_uid}'):
            return key.decode().split(':')[1]

        async for _ in self.redis_cli.iscan(match=f'ride:{user_uid}:passenger:*'):  # noqa
            return str(user_uid)

        return None

    async def expire(self, user_uid: str, role: str):
        await self.redis_cli.set(self.REMOVE_KEY.format(user_uid=user_uid), 'true')
        await asyncio.sleep(settings.USER_DATA_TTL_ON_CLOSE)
        if await self.redis_cli.get(self.REMOVE_KEY.format(user_uid=user_uid)):
            if role == constants.Role.HITCHHIKER:
                await self.exclude(user_uid)
            elif role == constants.Role.DRIVER:
                await self.delete(user_uid)
            await self.redis_cli.delete(self.REMOVE_KEY.format(user_uid=user_uid))

    async def unexpire(self, user_uid: str):
        await self.redis_cli.delete(self.REMOVE_KEY.format(user_uid=user_uid))


class StreamRepository:

    def __init__(self, redis_cli):
        self.redis_cli = redis_cli

    async def _produce(self, message_type: str, user_uid: str, payload: dict):
        await self.redis_cli.xadd(
            f'stream:{user_uid}',
            fields={
                'type': message_type,
                **payload,
            },
        )

    async def _broadcast(self, message_type: str, uids: typing.List[str], payload: dict):
        await asyncio.gather(*[self._produce(message_type, uid, payload) for uid in uids])

    async def ride_requested(self, ride_request: entities.RideRequest):
        await self._produce(
            constants.MessageType.RIDE_REQUESTED,
            user_uid=ride_request.receiver.uid,
            payload=schemas.RideRequestStreamSchema().dump(ride_request).data,
        )

    async def request_updated(self, ride_request: entities.RideRequest):
        event_map = {
            constants.RideRequestStatus.ACCEPTED: constants.MessageType.RIDE_REQUEST_ACCEPTED,
            constants.RideRequestStatus.DECLINED: constants.MessageType.RIDE_REQUEST_DECLINED,
        }
        await self._produce(
            event_map[ride_request.status],
            user_uid=ride_request.sender.uid,
            payload={
                'ride_uid': ride_request.ride_uid,
                'sender_uid': ride_request.sender.uid,
                'receiver_uid': ride_request.receiver.uid,
            },
        )

    async def ride_updated(self, ride: entities.Ride):
        user_uids = [passenger.profile.uid for passenger in ride.passengers]
        user_uids.append(ride.driver.uid)

        await self._broadcast(
            constants.MessageType.RIDE_UPDATED,
            user_uids,
            payload={
                'ride_uid': ride.uid,
            }
        )

    async def ride_cancelled(self, ride: entities.Ride):
        user_uids = [passenger.profile.uid for passenger in ride.passengers]

        await self._broadcast(
            constants.MessageType.RIDE_CANCELLED,
            user_uids,
            payload={
                'ride_uid': ride.uid,
            }
        )


class UserLocationRepository:
    KEY = 'user:locations'

    def __init__(self, redis_cli):
        self.redis_cli = redis_cli

    async def save(self, user_uid: str, location: entities.UserLocation):
        await self.redis_cli.geoadd(
            self.KEY,
            latitude=location.latitude,
            longitude=location.longitude,
            member=str(user_uid),
        )
        await self.redis_cli.hmset_dict(
            f'user:{user_uid}:location',
            user_uid=str(user_uid),
            latitude=location.latitude,
            longitude=location.longitude,
            course=location.course,
            ts=location.ts,
        )

    async def list(self, user_uid: str) -> typing.List[entities.UserLocation]:
        user_uid = str(user_uid)

        if await self.redis_cli.zrank(self.KEY, user_uid) is None:
            return []

        geomembers = await self.redis_cli.georadiusbymember(
            self.KEY,
            member=user_uid,
            radius=50,
            unit='km',
        )

        locations = await asyncio.gather(*[
            self.redis_cli.hgetall(f'user:{geomember.decode()}:location')
            for geomember in geomembers
        ])
        locations = [redis_utils.decode(location) for location in locations]

        schema = schemas.UserLocationRedisSchema(many=True).load(locations)
        if schema.errors:
            raise Exception(schema.errors)
        return schema.data

    async def delete(self, user_uid: str):
        await self.redis_cli.zrem(self.KEY, user_uid)
