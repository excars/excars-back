# pylint: disable=redefined-outer-name

import asyncio

import pytest


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_ride_requested(test_cli, add_jwt, create_user, user_to_redis):
    sender = create_user(username='georgy', first_name='George', last_name='Harrison')
    receiver = create_user(username='macca', first_name='Paul', last_name='McCartney')

    await user_to_redis(sender, role='driver')
    await user_to_redis(receiver, role='hitchhiker')

    url = await add_jwt('/stream', user_uid=receiver.uid)
    conn = await test_cli.ws_connect(url)

    try:
        await conn.receive_json(timeout=0.1)
    except asyncio.TimeoutError:
        pass

    await test_cli.app.redis.xadd(
        stream=f'stream:{receiver.uid}',
        fields={
            'type': 'RIDE_REQUESTED',
            'ride_uid': f'{sender.uid}',
            'sender_uid': f'{sender.uid}',
            'receiver_uid': f'{receiver.uid}',
        }
    )

    response = await conn.receive_json(timeout=0.2)

    assert 'type' in response


@pytest.mark.require_db
@pytest.mark.require_redis
async def test_ride_request_updated(test_cli, add_jwt, create_user, user_to_redis):
    sender = create_user(username='georgy', first_name='George', last_name='Harrison')
    receiver = create_user(username='macca', first_name='Paul', last_name='McCartney')

    await user_to_redis(sender, role='driver')
    await user_to_redis(receiver, role='hitchhiker')

    url = await add_jwt('/stream', user_uid=sender.uid)
    conn = await test_cli.ws_connect(url)

    try:
        await conn.receive_json(timeout=0.1)
    except asyncio.TimeoutError:
        pass

    await test_cli.app.redis.xadd(
        stream=f'stream:{sender.uid}',
        fields={
            'type': 'RIDE_REQUEST_ACCEPTED',
            'ride_uid': f'{sender.uid}',
            'sender_uid': f'{sender.uid}',
            'receiver_uid': f'{receiver.uid}',
        }
    )

    response = await conn.receive_json(timeout=0.2)

    assert 'type' in response
