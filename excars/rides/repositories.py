import asyncio
import typing

from excars import redis as redis_utils

from . import constants, entities, schemas


class ProfileRepository:

    def __init__(self, redis_cli):
        self.redis_cli = redis_cli

    async def save(self, profile: entities.Profile):
        await self.redis_cli.hmset_dict(
            f'user:{profile.uid}',
            **schemas.ProfileRedisSchema().dump(profile).data
        )

    async def get(self, user_uid: str) -> typing.Optional[entities.Profile]:
        payload = redis_utils.decode(await self.redis_cli.hgetall(f'user:{user_uid}'))

        data, errors = schemas.ProfileRedisSchema().load(payload)
        if errors:
            return None

        return data


class RideRepository:

    def __init__(self, redis_cli):
        self.redis_cli = redis_cli

    async def add(self, ride_request: entities.RideRequest):
        await self.redis_cli.hmset_dict(
            f'ride:{ride_request.ride_uid}',
            {
                ride_request.passenger.uid: ride_request.status
            },
        )

    async def exists(self, ride_request: entities.RideRequest) -> bool:
        return bool(await self.redis_cli.hexists(
            f'ride:{ride_request.ride_uid}',
            ride_request.passenger.uid
        ))

    async def get(self, ride_uid: str) -> entities.Ride:
        payload = redis_utils.decode(await self.redis_cli.hgetall(f'ride:{ride_uid}'))

        profile_repo = ProfileRepository(self.redis_cli)
        driver = await profile_repo.get(ride_uid)
        passengers = await asyncio.gather(*[profile_repo.get(user_uid) for user_uid in payload])

        return entities.Ride(uid=ride_uid, driver=driver, passengers=passengers)


class StreamRepository:

    def __init__(self, redis_cli):
        self.redis_cli = redis_cli

    async def _produce(self, message_type, user_uid, payload):
        await self.redis_cli.xadd(
            f'stream:{user_uid}',
            fields={
                'type': message_type,
                **payload,
            },
        )

    async def ride_requested(self, ride_request: entities.RideRequest):
        await self._produce(
            constants.MessageType.RIDE_REQUESTED,
            user_uid=str(ride_request.receiver),
            payload=schemas.RideRequestStreamSchema().dump(ride_request).data,
        )

    async def ride_updated(self, ride_request: entities.RideRequest):
        event_map = {
            constants.RideRequestStatus.ACCEPTED: constants.MessageType.RIDE_ACCEPTED,
            constants.RideRequestStatus.DECLINED: constants.MessageType.RIDE_DECLINED,
        }
        await self._produce(
            event_map[ride_request.status],
            user_uid=str(ride_request.receiver),
            payload={
                'ride_uid': ride_request.ride_uid,
                'sender_uid': ride_request.sender.uid,
                'receiver_uid': ride_request.receiver.uid,
            },
        )


class UserLocationRepository:
    TTL = 60 * 30

    def __init__(self, redis_cli):
        self.redis_cli = redis_cli

    async def save(self, user, location: entities.UserLocation):
        key = f'user:location:{user.uid}'
        await self.redis_cli.hmset_dict(
            key,
            **schemas.UserLocationSchema().dump(location).data
        )
        await self.redis_cli.expire(key, self.TTL)

    async def list(self, exclude: typing.Optional[str] = None) -> typing.List[entities.UserLocation]:
        payload = await asyncio.gather(
            *[
                self.redis_cli.hgetall(k)
                async for k in self.redis_cli.iscan(match='user:location:*')
                if k != f'user:location:{exclude}'.encode()
            ],
            return_exceptions=True
        )

        payload = map(redis_utils.decode, payload)

        location_list, errors = schemas.UserLocationSchema().load(payload, many=True)
        if errors:
            return []

        return location_list
