# pylint: disable=redefined-outer-name

import pytest

from . import constants

@pytest.fixture
def join_payload():
    def wrapper(role):
        return {
            'role': role,
            'destination': {
                'name': 'Porto Bello',
                'latitude': constants.DEFAULT_LAT,
                'longitude': constants.DEFAULT_LONG,
            },
        }
    return wrapper


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_join(test_cli, add_jwt, create_user, join_payload):
    user = create_user()
    url = await add_jwt('/api/rides/join', user_uid=user.uid)

    response = await test_cli.post(url, json=join_payload('driver'))

    assert response.status == 200

    redis_cli = test_cli.app.redis
    profile = await redis_cli.hgetall(f'user:{user.uid}')

    assert profile[b'role'] == b'driver'
    assert profile[b'dest_name'] == b'Porto Bello'
    assert profile[b'dest_lat'] == str(constants.DEFAULT_LAT).encode()
    assert profile[b'dest_lon'] == str(constants.DEFAULT_LONG).encode()


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_join_invalid_role(test_cli, add_jwt, create_user, join_payload):
    user = create_user()
    url = await add_jwt('/api/rides/join', user_uid=user.uid)

    response = await test_cli.post(url, json=join_payload('collector'))

    assert response.status == 400

    redis_cli = test_cli.app.redis
    profile = await redis_cli.hgetall(f'user:{user.uid}')

    assert profile == {}


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_retrieve_profile(test_cli, create_user, add_jwt, user_to_redis):
    user = create_user(first_name='John', last_name='Lennon')
    await user_to_redis(user, role='driver')

    url = await add_jwt(f'/api/profiles/{user.uid}', user_uid=str(user.uid))
    response = await test_cli.get(url)
    assert response.status == 200

    content = await response.json()
    assert content == {
        'uid': str(user.uid),
        'name': 'John Lennon',
        'avatar': '',
        'plate': '',
        'role': 'driver',
        'destination': {
            'name': 'Porto Bello',
            'latitude': constants.DEFAULT_LAT,
            'longitude': constants.DEFAULT_LONG,
        },
    }


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_retrieve_profile_for_non_joined_user(test_cli, create_user, add_jwt):
    user = create_user(first_name='John', last_name='Lennon')

    url = await add_jwt(f'/api/profiles/{user.uid}', user_uid=str(user.uid))
    response = await test_cli.get(url)
    assert response.status == 404


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_retrieve_me(test_cli, create_user, add_jwt, user_to_redis):
    user = create_user(first_name='Ringo', last_name='Starr')
    await user_to_redis(user, role='driver')

    url = await add_jwt(f'/api/profiles/me', user_uid=user.uid)
    response = await test_cli.get(url)
    assert response.status == 200

    content = await response.json()
    assert content == {
        'uid': str(user.uid),
        'name': 'Ringo Starr',
        'avatar': '',
        'plate': '',
        'role': 'driver',
        'destination': {
            'name': 'Porto Bello',
            'latitude': constants.DEFAULT_LAT,
            'longitude': constants.DEFAULT_LONG,
        },
    }


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_retrieve_me_for_non_joined_user(test_cli, create_user, add_jwt):
    user = create_user(first_name='Ringo', last_name='Starr')

    url = await add_jwt(f'/api/profiles/me', user_uid=user.uid)
    response = await test_cli.get(url)
    assert response.status == 200

    content = await response.json()
    assert content == {
        'uid': str(user.uid),
        'name': 'Ringo Starr',
        'avatar': '',
        'plate': '',
        'destination': None,
        'role': None,
    }


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_driver_creates_ride(test_cli, create_user, add_jwt, user_to_redis):
    sender = create_user(username='georgy', first_name='George', last_name='Harrison')
    receiver = create_user(username='macca', first_name='Paul', last_name='McCartney')

    await user_to_redis(sender, role='driver')
    await user_to_redis(receiver, role='hitchhiker')

    url = await add_jwt(f'/api/rides', user_uid=sender.uid)

    response = await test_cli.post(url, json={
        'receiver': str(receiver.uid)
    })

    assert response.status == 200

    redis_cli = test_cli.app.redis
    assert await redis_cli.get(f'ride:{sender.uid}:request:{receiver.uid}') == b'requested'


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_hitchhiker_creates_ride(test_cli, create_user, add_jwt, user_to_redis):
    sender = create_user(username='georgy', first_name='George', last_name='Harrison')
    receiver = create_user(username='macca', first_name='Paul', last_name='McCartney')

    await user_to_redis(sender, role='hitchhiker')
    await user_to_redis(receiver, role='driver')

    url = await add_jwt(f'/api/rides', user_uid=sender.uid)

    response = await test_cli.post(url, json={
        'receiver': str(receiver.uid)
    })

    assert response.status == 200

    redis_cli = test_cli.app.redis
    assert await redis_cli.get(f'ride:{receiver.uid}:request:{sender.uid}') == b'requested'


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_driver_updates_ride(test_cli, create_user, add_jwt, user_to_redis, ride_request_to_redis):
    sender = create_user(username='georgy', first_name='George', last_name='Harrison')
    receiver = create_user(username='macca', first_name='Paul', last_name='McCartney')

    await user_to_redis(sender, role='driver')
    await user_to_redis(receiver, role='hitchhiker')
    await ride_request_to_redis(driver_uid=sender.uid, passenger_uid=receiver.uid)

    ride_uid = sender.uid
    url = await add_jwt(f'/api/rides/{ride_uid}', user_uid=sender.uid)

    response = await test_cli.put(url, json={
        'status': 'accepted',
        'passenger_uid': str(receiver.uid),
    })

    assert response.status == 200

    assert await test_cli.app.redis.exists(f'ride:{sender.uid}:request:{receiver.uid}') == 0
    assert await test_cli.app.redis.get(f'ride:{sender.uid}:passenger:{receiver.uid}') == b'accepted'


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_hitchhiker_updates_ride(test_cli, create_user, add_jwt, user_to_redis, ride_request_to_redis):
    sender = create_user(username='georgy', first_name='George', last_name='Harrison')
    receiver = create_user(username='macca', first_name='Paul', last_name='McCartney')

    await user_to_redis(sender, role='hitchhiker')
    await user_to_redis(receiver, role='driver')
    await ride_request_to_redis(driver_uid=receiver.uid, passenger_uid=sender.uid)

    ride_uid = receiver.uid
    url = await add_jwt(f'/api/rides/{ride_uid}', user_uid=sender.uid)

    response = await test_cli.put(url, json={
        'status': 'accepted',
    })

    assert response.status == 200

    assert await test_cli.app.redis.exists(f'ride:{receiver.uid}:request:{sender.uid}') == 0
    assert await test_cli.app.redis.get(f'ride:{receiver.uid}:passenger:{sender.uid}') == b'accepted'


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_current_ride(test_cli, create_user, add_jwt, user_to_redis):
    sender = create_user(username='georgy', first_name='George', last_name='Harrison')
    receiver = create_user(username='macca', first_name='Paul', last_name='McCartney')

    await user_to_redis(sender, role='driver')
    await user_to_redis(receiver, role='hitchhiker', ride_uid=sender.uid)

    ride_uid = str(sender.uid)
    url = await add_jwt(f'/api/rides/current', user_uid=sender.uid)

    response = await test_cli.get(url)

    assert response.status == 200

    assert await response.json() == {
        'uid': ride_uid,
        'driver': {
            'uid': str(sender.uid),
            'name': 'George Harrison',
            'role': 'driver',
            'plate': '',
            'avatar': '',
            'destination': {
                'name': 'Porto Bello',
                'latitude': constants.DEFAULT_LAT,
                'longitude': constants.DEFAULT_LONG,
            },
        },
        'passengers': [
            {
                'profile': {
                    'uid': str(receiver.uid),
                    'name': 'Paul McCartney',
                    'role': 'hitchhiker',
                    'avatar': '',
                    'plate': '',
                    'destination': {
                        'name': 'Porto Bello',
                        'latitude': constants.DEFAULT_LAT,
                        'longitude': constants.DEFAULT_LONG,
                    },
                },
                'status': 'accepted',
            },
        ],
    }
