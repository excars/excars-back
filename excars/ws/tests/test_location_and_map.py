import asyncio

import pytest


async def fake_coro():
    return


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_publish_location(test_cli, add_jwt, mocker):
    mocker.patch('excars.ws.consumers.init', lambda *args, **kwargs: fake_coro())
    url = await add_jwt('/stream')
    conn = await test_cli.ws_connect(url)
    await conn.send_json({'data': {'longitude': 1, 'latitude': 1, 'course': -1}, 'type': 'LOCATION'})

    with pytest.raises(asyncio.TimeoutError):
        await conn.receive_json(timeout=0.2)


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_publish_location_users_with_no_distance(test_cli, add_jwt, create_user, mocker):
    mocker.patch('excars.ws.consumers.init', lambda *args, **kwargs: fake_coro())

    user_1 = create_user(username='1')
    conn_user_1 = await test_cli.ws_connect(
        await add_jwt('/stream', user_uid=user_1.uid)
    )
    await conn_user_1.send_json({'data': {'longitude': 0, 'latitude': 0, 'course': -1}, 'type': 'LOCATION'})

    user_2 = create_user(username='2')
    conn_user_2 = await test_cli.ws_connect(
        await add_jwt('/stream', user_uid=user_2.uid)
    )
    await conn_user_2.send_json({'data': {'longitude': 0.02, 'latitude': 0, 'course': -1}, 'type': 'LOCATION'})

    user_3 = create_user(username='3')
    conn_user_3 = await test_cli.ws_connect(
        await add_jwt('/stream', user_uid=user_3.uid)
    )

    locations = await conn_user_2.receive_json()
    assert locations['type'] == 'MAP'
    assert len(locations['data']) == 2
    uids = [i['user_uid'] for i in locations['data']]
    assert str(user_1.uid) in uids
    assert str(user_2.uid) in uids

    user_data = locations['data'][0]
    assert {'user_uid', 'longitude', 'latitude', 'course'} == set(user_data.keys())

    with pytest.raises(asyncio.TimeoutError):
        await conn_user_3.receive_json(timeout=0.2)
