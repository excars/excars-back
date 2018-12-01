import pytest


async def fake_coro():
    return


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_publish_location(test_cli, add_jwt, mocker):
    mocker.patch('excars.ws.consumers.init', lambda *args, **kwargs: fake_coro())
    url = await add_jwt('/stream')
    conn = await test_cli.ws_connect(url)
    await conn.send_json({'data': {'longitude': 1, 'latitude': 1}, 'type': 'LOCATION'})
    locations = await conn.receive_json()
    assert locations == {'data': [], 'type': 'MAP'}


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_publish_location_users_with_no_distance(test_cli, add_jwt, create_user, mocker):
    mocker.patch('excars.ws.consumers.init', lambda *args, **kwargs: fake_coro())

    user_1 = create_user(username='1')
    conn_user_1 = await test_cli.ws_connect(
        await add_jwt('/stream', user_id=user_1.id)
    )
    await conn_user_1.send_json({'data': {'longitude': 0, 'latitude': 0}, 'type': 'LOCATION'})

    user_2 = create_user(username='2')
    conn_user_2 = await test_cli.ws_connect(
        await add_jwt('/stream', user_id=user_2.id)
    )
    await conn_user_2.send_json({'data': {'longitude': 0.02, 'latitude': 0}, 'type': 'LOCATION'})

    user_3 = create_user(username='3')
    conn_user_3 = await test_cli.ws_connect(
        await add_jwt('/stream', user_id=user_3.id)
    )

    locations = await conn_user_3.receive_json()
    assert locations['type'] == 'MAP'
    assert len(locations['data']) == 2
    uids = [i['uid'] for i in locations['data']]
    assert str(user_1.uid) in uids
    assert str(user_2.uid) in uids

    user_data = locations['data'][0]
    assert user_data['distance'] is None
    assert {'uid', 'distance', 'longitude', 'latitude', 'last'} == set(user_data.keys())


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_publish_location_users_with_distance(test_cli, add_jwt, create_user, mocker):
    mocker.patch('excars.ws.consumers.init', lambda *args, **kwargs: fake_coro())

    user_1 = create_user(username='1')
    conn_user_1 = await test_cli.ws_connect(
        await add_jwt('/stream', user_id=user_1.id)
    )
    await conn_user_1.send_json({'data': {'longitude': .01, 'latitude': .01}, 'type': 'LOCATION'})

    user_2 = create_user(username='2')
    conn_user_2 = await test_cli.ws_connect(
        await add_jwt('/stream', user_id=user_2.id)
    )
    await conn_user_2.send_json({'data': {'longitude': .02, 'latitude': .01}, 'type': 'LOCATION'})

    locations = await conn_user_1.receive_json()
    assert locations['type'] == 'MAP'
    uids = [i['uid'] for i in locations['data']]
    assert len(locations['data']) == 1
    assert str(user_2.uid) in uids

    user_data = locations['data'][0]
    assert user_data['distance'] is not None
    assert {'uid', 'distance', 'longitude', 'latitude', 'last'} == set(user_data.keys())
