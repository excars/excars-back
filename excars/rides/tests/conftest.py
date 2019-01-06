import pytest

from . import constants


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
            dest_lat=constants.DEFAULT_LAT,
            dest_lon=constants.DEFAULT_LONG,
        )
        await test_cli.app.redis.geoadd(
            'user:locations',
            member=str(user.uid),
            latitude=constants.DEFAULT_LAT,
            longitude=constants.DEFAULT_LONG,
        )
        await test_cli.app.redis.hmset_dict(
            f'user:{user.uid}:location',
            user_uid=str(user.uid),
            latitude=constants.DEFAULT_LAT,
            longitude=constants.DEFAULT_LONG,
            course=1,
            ts=1546784075.0,
        )
        if ride_uid and ride_uid != str(user.uid):
            await test_cli.app.redis.set(f'ride:{ride_uid}:passenger:{user.uid}', 'accepted')

    return wrapper


@pytest.fixture
def ride_request_to_redis(test_cli):
    async def wrapper(driver_uid, passenger_uid):
        await test_cli.app.redis.set(f'ride:{driver_uid}:request:{passenger_uid}', 'requested')
    return wrapper
