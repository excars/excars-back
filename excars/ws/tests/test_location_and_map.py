import asyncio

import pytest


async def fake_coro():
    return


@pytest.fixture
def user_to_redis(test_cli):
    async def wrapper(user):
        await test_cli.app.redis.hmset_dict(
            f'user:{user.uid}',
            uid=str(user.uid),
            name=user.get_name(),
            avatar=user.avatar,
            plate=user.plate,
            role='driver',
            dest_name='Porto Bello',
            dest_lat=34.6709681,
            dest_lon=33.0396582,
        )
    return wrapper


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_publish_location(test_cli, add_jwt, mocker):
    mocker.patch('excars.ws.consumers.init', lambda *args, **kwargs: fake_coro())
    url = await add_jwt('/stream')
    conn = await test_cli.ws_connect(url)
    await conn.send_json({'data': {'longitude': 1, 'latitude': 1, 'course': -1}, 'type': 'LOCATION'})

    with pytest.raises(asyncio.TimeoutError):
        await conn.receive_json(timeout=0.2)
