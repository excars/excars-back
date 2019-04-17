import asyncio
import uuid

import pytest


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_ride_undo_remove_connect(test_cli, add_jwt, create_user, user_to_redis):

    driver = create_user(uid=uuid.uuid4())
    await user_to_redis(driver, role="driver")

    await test_cli.app.redis.expire(f"user:{driver.uid}", 2)
    await test_cli.app.redis.set(f"remove:ride:{driver.uid}", "true")

    url = await add_jwt("/stream", user_uid=driver.uid)
    await test_cli.ws_connect(url)

    await asyncio.sleep(0.1)

    assert await test_cli.app.redis.ttl(f"user:{driver.uid}") == -1
    assert await test_cli.app.redis.get(f"remove:ride:{driver.uid}") is None


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_connect_smoke(test_cli, add_jwt, create_user, user_to_redis):
    driver = create_user(uid=uuid.uuid4())
    await user_to_redis(driver, role="driver")

    url = await add_jwt("/stream", user_uid=driver.uid)
    await test_cli.ws_connect(url)

    await asyncio.sleep(0.1)

    assert await test_cli.app.redis.ttl(f"user:{driver.uid}") == -1
    assert await test_cli.app.redis.get(f"remove:ride:{driver.uid}") is None


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_connect_smoke_no_role(test_cli, add_jwt, create_user):
    user = create_user(uid=uuid.uuid4())

    url = await add_jwt("/stream", user_uid=user.uid)
    await test_cli.ws_connect(url)

    await asyncio.sleep(0.1)

    assert await test_cli.app.redis.ttl(f"user:{user.uid}") == -2
    assert await test_cli.app.redis.get(f"remove:ride:{user.uid}") is None


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_stream_disconnect_driver(test_cli, add_jwt, create_user, user_to_redis):

    driver = create_user(uid=uuid.uuid4())
    await user_to_redis(driver, role="driver")

    passenger = create_user(uid=uuid.uuid4())
    await user_to_redis(passenger, role="hitchhiker", ride_uid=driver.uid)

    url = await add_jwt("/stream", user_uid=driver.uid)
    conn = await test_cli.ws_connect(url)
    await asyncio.sleep(0.1)

    await conn.close()
    await asyncio.sleep(1)

    assert await test_cli.app.redis.exists(f"user:{passenger.uid}")
    assert not await test_cli.app.redis.exists(f"user:{driver.uid}")
    assert not await test_cli.app.redis.exists(f"ride:{driver.uid}:passenger:{passenger.uid}")


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_stream_disconnect_passenger(test_cli, add_jwt, create_user, user_to_redis):

    driver = create_user(uid=uuid.uuid4())
    await user_to_redis(driver, role="driver")

    passenger = create_user(uid=uuid.uuid4())
    await user_to_redis(passenger, role="hitchhiker", ride_uid=driver.uid)
    passenger2 = create_user(uid=uuid.uuid4())
    await user_to_redis(passenger2, role="hitchhiker", ride_uid=driver.uid)

    url = await add_jwt("/stream", user_uid=passenger.uid)
    passenger_conn = await test_cli.ws_connect(url)

    await asyncio.sleep(0.1)

    await passenger_conn.close()
    await asyncio.sleep(1)

    assert not await test_cli.app.redis.exists(f"user:{passenger.uid}")
    assert not await test_cli.app.redis.exists(f"ride:{driver.uid}:passenger:{passenger.uid}")

    assert await test_cli.app.redis.exists(f"user:{driver.uid}")
    assert await test_cli.app.redis.exists(f"user:{passenger2.uid}")
    assert await test_cli.app.redis.exists(f"ride:{driver.uid}:passenger:{passenger2.uid}")


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_stream_disconnect_with_reconnect(test_cli, add_jwt, create_user, user_to_redis, mocker):
    mocker.patch("excars.settings.PUBLISH_MAP_FREQUENCY", 100)

    mocker.patch("excars.settings.USER_DATA_TTL_ON_CLOSE", 1)

    driver = create_user(uid=uuid.uuid4())
    await user_to_redis(driver, role="driver")

    passenger = create_user(uid=uuid.uuid4())
    await user_to_redis(passenger, role="hitchhiker", ride_uid=driver.uid)
    passenger2 = create_user(uid=uuid.uuid4())
    await user_to_redis(passenger2, role="hitchhiker", ride_uid=driver.uid)

    url = await add_jwt("/stream", user_uid=passenger.uid)
    passenger_conn = await test_cli.ws_connect(url)

    await asyncio.sleep(0.1)

    await passenger_conn.close()
    await asyncio.sleep(0.5)

    await test_cli.ws_connect(url)

    assert await test_cli.app.redis.exists(f"user:{passenger.uid}")
    assert await test_cli.app.redis.exists(f"ride:{driver.uid}:passenger:{passenger.uid}")

    assert await test_cli.app.redis.exists(f"user:{driver.uid}")
    assert await test_cli.app.redis.exists(f"user:{passenger2.uid}")
    assert await test_cli.app.redis.exists(f"ride:{driver.uid}:passenger:{passenger2.uid}")
