# pylint: disable=redefined-outer-name

import uuid

import pytest


@pytest.fixture
def join_payload():
    def wrapper(role):
        return {
            'role': role,
            'destination': {
                'name': 'Porto Bello',
                'latitude': 34.6709681,
                'longitude': 33.0396582,
            },
        }
    return wrapper


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


@pytest.fixture
def ride_to_redis(test_cli):
    async def wrapper(ride_uid, sender_uid, receiver_uid):
        await test_cli.app.redis.hmset_dict(
            f'ride:{ride_uid}',
            uid=str(ride_uid),
            sender=str(sender_uid),
            receiver=str(receiver_uid),
        )
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
    assert profile[b'dest_lat'] == b'34.6709681'
    assert profile[b'dest_lon'] == b'33.0396582'


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
    await user_to_redis(user)

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
            'latitude': 34.6709681,
            'longitude': 33.0396582,
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
    await user_to_redis(user)

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
            'latitude': 34.6709681,
            'longitude': 33.0396582,
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
async def test_create_ride(test_cli, create_user, add_jwt, user_to_redis):
    sender = create_user(username='georgy', first_name='George', last_name='Harrison')
    receiver = create_user(username='macca', first_name='Paul', last_name='McCartney')

    await user_to_redis(sender)
    await user_to_redis(receiver)

    url = await add_jwt(f'/api/rides', user_uid=sender.uid)

    response = await test_cli.post(url, json={
        'receiver': str(receiver.uid)
    })

    assert response.status == 200


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_create_ride_receiver_does_not_exists(test_cli, create_user, add_jwt, user_to_redis):
    sender = create_user(username='georgy', first_name='George', last_name='Harrison')
    receiver = create_user(username='macca', first_name='Paul', last_name='McCartney')

    await user_to_redis(sender)

    url = await add_jwt(f'/api/rides', user_uid=sender.uid)

    response = await test_cli.post(url, json={
        'receiver': str(receiver.uid)
    })

    assert response.status == 404


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_update_ride(test_cli, create_user, add_jwt, ride_to_redis):
    sender = create_user(username='georgy', first_name='George', last_name='Harrison')
    receiver = create_user(username='macca', first_name='Paul', last_name='McCartney')

    ride_uid = uuid.uuid4()
    await ride_to_redis(ride_uid, sender.uid, receiver.uid)

    url = await add_jwt(f'/api/rides/{ride_uid}', user_uid=receiver.uid)

    response = await test_cli.put(url, json={
        'status': 'accept'
    })

    assert response.status == 200


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_update_ride_does_not_exists(test_cli, add_jwt):
    ride_uid = uuid.uuid4()

    url = await add_jwt(f'/api/rides/{ride_uid}')

    response = await test_cli.put(url, json={
        'status': 'accept'
    })

    assert response.status == 404
