import pytest


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_join(test_cli, add_jwt, create_user):
    user = create_user()
    url = await add_jwt('/api/rides/join', user_id=user.id)

    response = await test_cli.post(
        url,
        json={
            'role': 'driver',
            'destination': {
                'name': 'Porto Bello',
                'latitude': 34.6709681,
                'longitude': 33.0396582,
            },
        }
    )

    assert response.status == 200

    redis_cli = test_cli.app.redis
    profile = await redis_cli.hgetall(f'user:{user.uid}')

    assert profile[b'role'] == b'driver'


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_retrieve_profile(test_cli, create_user, add_jwt):
    user = create_user(first_name='John', last_name='Lennon')

    redis_cli = test_cli.app.redis
    await redis_cli.hmset_dict(
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

    url = await add_jwt(f'/api/profiles/{user.uid}', user_id=str(user.id))
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
