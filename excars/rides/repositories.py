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

    async def save(self, ride: entities.Ride):
        await self.redis_cli.hmset_dict(
            f'ride:{ride.uid}',
            **schemas.RideRedisSchema().dump(ride).data
        )

    async def get(self, ride_uid: str) -> typing.Optional[entities.Ride]:
        payload = redis_utils.decode(await self.redis_cli.hgetall(f'ride:{ride_uid}'))

        data, errors = schemas.RideRedisSchema().load(payload)
        if errors:
            return None

        return data


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

    async def request_ride(self, ride: entities.Ride):
        await self._produce(
            constants.MessageType.RIDE_REQUESTED,
            user_uid=str(ride.receiver),
            payload=schemas.RideStreamSchema().dump(ride).data,
        )

    async def update_ride(self, ride: entities.Ride, status: str):
        event_map = {
            'accept': constants.MessageType.RIDE_ACCEPTED,
            'decline': constants.MessageType.RIDE_DECLINED,
            'cancel': constants.MessageType.RIDE_CANCELLED,
        }
        await self._produce(
            event_map[status],
            user_uid=str(ride.sender),
            payload=schemas.RideStreamSchema().dump(ride).data,
        )
