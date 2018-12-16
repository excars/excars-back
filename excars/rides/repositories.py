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

    async def create_request(self, ride_request: entities.RideRequest):
        await self.redis_cli.setex(
            f'ride:{ride_request.ride_uid}:request:{ride_request.passenger.uid}',
            value=ride_request.status,
            seconds=30,
        )

    async def update_request(self, ride_request: entities.RideRequest):
        ride_key = f'ride:{ride_request.ride_uid}'
        await self.redis_cli.delete(f'{ride_key}:request:{ride_request.passenger.uid}')

        status = ride_request.status
        await self.redis_cli.set(f'{ride_key}:passenger:{ride_request.passenger.uid}', status)

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

        return entities.Ride(uid=ride_uid, driver=driver, passengers=passengers)

    async def get_ride_uid(self, user_uid: str) -> typing.Optional[str]:
        async for key in self.redis_cli.iscan(match=f'ride:*:passenger:{user_uid}'):
            return key.decode().split(':')[1]

        async for _ in self.redis_cli.iscan(match=f'ride:*{user_uid}*'):  # noqa
            return str(user_uid)

        return None


class StreamRepository:

    def __init__(self, redis_cli):
        self.redis_cli = redis_cli

    async def _produce(self, message_type, user_uid: str, payload):
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
            user_uid=ride_request.receiver.uid,
            payload=schemas.RideRequestStreamSchema().dump(ride_request).data,
        )

    async def ride_updated(self, ride_request: entities.RideRequest):
        event_map = {
            constants.RideRequestStatus.ACCEPTED: constants.MessageType.RIDE_ACCEPTED,
            constants.RideRequestStatus.DECLINED: constants.MessageType.RIDE_DECLINED,
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


class UserLocationRepository:
    KEY = 'user:locations'
    TTL = 60 * 30

    def __init__(self, redis_cli):
        self.redis_cli = redis_cli

    async def save(self, user, location: entities.UserLocation):
        await self.redis_cli.geoadd(
            self.KEY,
            latitude=location.latitude,
            longitude=location.longitude,
            member=str(user.uid),
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
            with_coord=True,
        )

        return schemas.UserLocationRedisSchema(many=True).dump(geomembers).data
