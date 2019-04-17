import time
import uuid

import pytest

from . import constants


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_publish_map_with_same_ride(test_cli, create_user, add_jwt, user_to_redis):
    driver = create_user(username="lennie", first_name="John", last_name="Lennon")
    passenger = create_user(username="georgy", first_name="George", last_name="Harrison")

    await user_to_redis(driver, role="driver")
    await user_to_redis(passenger, role="hitchhiker", ride_uid=driver.uid)

    url = await add_jwt("/stream", user_uid=driver.uid)
    conn = await test_cli.ws_connect(url)

    locations = await conn.receive_json(timeout=0.3)

    assert locations["data"] == [
        {
            "user_uid": str(passenger.uid),
            "role": "hitchhiker",
            "location": {
                "user_uid": str(passenger.uid),
                "latitude": constants.DEFAULT_LAT,
                "longitude": constants.DEFAULT_LONG,
                "course": 1.0,
                "ts": 1546784075.0,
            },
            "has_same_ride": True,
        }
    ]


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_publish_map_different_ride(test_cli, create_user, add_jwt, user_to_redis):
    driver = create_user(username="lennie", first_name="John", last_name="Lennon")
    passenger = create_user(username="georgy", first_name="George", last_name="Harrison")

    await user_to_redis(driver, role="driver", ride_uid=None)
    await user_to_redis(passenger, role="hitchhiker", ride_uid=uuid.uuid4())

    url = await add_jwt("/stream", user_uid=driver.uid)
    conn = await test_cli.ws_connect(url)

    assert await conn.receive_json(timeout=0.3) == {"data": [], "type": "MAP"}


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_publish_map_no_ride(test_cli, create_user, add_jwt, user_to_redis):
    driver = create_user(username="lennie", first_name="John", last_name="Lennon")
    hitchhiker = create_user(username="georgy", first_name="George", last_name="Harrison")

    await user_to_redis(driver, role="driver", ride_uid=None)
    await user_to_redis(hitchhiker, role="hitchhiker", ride_uid=None)

    url = await add_jwt("/stream", user_uid=driver.uid)
    conn = await test_cli.ws_connect(url)

    locations = await conn.receive_json(timeout=0.3)

    assert locations["data"] == [
        {
            "user_uid": str(hitchhiker.uid),
            "role": "hitchhiker",
            "location": {
                "user_uid": str(hitchhiker.uid),
                "latitude": constants.DEFAULT_LAT,
                "longitude": constants.DEFAULT_LONG,
                "course": 1.0,
                "ts": 1546784075.0,
            },
            "has_same_ride": False,
        }
    ]


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_publish_map_no_profile(test_cli, create_user, add_jwt, user_to_redis):
    user = create_user(username="lennie", first_name="John", last_name="Lennon")
    hitchhiker = create_user(username="georgy", first_name="George", last_name="Harrison")

    await test_cli.app.redis.geoadd(
        "user:locations", member=str(user.uid), latitude=constants.DEFAULT_LAT, longitude=constants.DEFAULT_LONG
    )
    await test_cli.app.redis.hmset_dict(
        f"user:{user.uid}:location",
        user_uid=str(user.uid),
        latitude=constants.DEFAULT_LAT,
        longitude=constants.DEFAULT_LONG,
        course=-1,
        ts=time.time(),
    )
    await user_to_redis(hitchhiker, role="hitchhiker", ride_uid=None)

    url = await add_jwt("/stream", user_uid=user.uid)
    conn = await test_cli.ws_connect(url)

    locations = await conn.receive_json(timeout=0.3)

    assert locations["data"] == [
        {
            "user_uid": str(hitchhiker.uid),
            "role": "hitchhiker",
            "location": {
                "user_uid": str(hitchhiker.uid),
                "latitude": constants.DEFAULT_LAT,
                "longitude": constants.DEFAULT_LONG,
                "course": 1.0,
                "ts": 1546784075.0,
            },
            "has_same_ride": False,
        }
    ]
