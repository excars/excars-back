import pytest


@pytest.fixture
def user_to_redis(test_cli):
    async def wrapper(user, role, ride_uid=None):
        await test_cli.app.redis.hmset_dict(
            f'user:{user.uid}',
            uid=str(user.uid),
            name=user.get_name(),
            avatar=user.avatar,
            plate=user.plate,
            role=role,
            dest_name='Porto Bello',
            dest_lat=34.6709681,
            dest_lon=33.0396582,
        )
        await test_cli.app.redis.geoadd(
            'user:locations',
            member=str(user.uid),
            latitude=34.67096919407988,
            longitude=33.039657175540924,
        )
        if ride_uid:
            await test_cli.app.redis.set(f'ride:user:{user.uid}', str(ride_uid))
    return wrapper


@pytest.fixture
def ride_to_redis(test_cli):
    async def wrapper(driver_uid, passenger_uid, status='requested'):
        await test_cli.app.redis.hmset_dict(
            f'ride:{driver_uid}',
            {
                str(passenger_uid): status
            },
        )
    return wrapper
