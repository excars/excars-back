# pylint: disable=redefined-outer-name

import aioredis
import pytest

from excars.settings import redis as redis_settings


@pytest.fixture(scope='session')
async def redis():
    redis_cli = await aioredis.create_redis_pool(
        redis_settings.REDIS_URL,
        db=15,
        minsize=redis_settings.REDIS_POOL_MIN,
        maxsize=redis_settings.REDIS_POOL_MAX,
    )

    yield redis_cli

    redis_cli.close()
    await redis_cli.wait_closed()


@pytest.fixture(scope='function')
async def require_redis(test_cli, redis):
    test_cli.app.redis = redis
    await test_cli.app.redis.flushdb()

    yield

    del test_cli.app.redis


@pytest.fixture(autouse=True)
def _require_redis_marker(request):
    marker = request.node.get_closest_marker('require_redis')
    if marker:
        return request.getfixturevalue('require_redis')
    return None
