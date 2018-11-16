import asyncio

import ujson

from .. import event
from ..utils import USER_PREFIX

PUB_LOCATION_FREQUENCY = 5
EVENT = 'MAP'


@event.publisher
async def handler(request, ws):
    while True:
        data = await get_users_data(request['user'], request.app.redis)
        if data is None:
            await asyncio.sleep(1)
            continue
        message = {'type': EVENT, 'data': data}
        await ws.send(ujson.dumps(message))
        await asyncio.sleep(PUB_LOCATION_FREQUENCY)


async def get_users_data(user, redis):
    users_info = await asyncio.gather(
        *[redis.hgetall(k) async for k in redis.iscan(match=f'{USER_PREFIX}*')],
        return_exceptions=True
    )
    if not users_info or user.encode() not in [_data[b'uid'] for _data in users_info]:
        return
    distances = await get_users_distances(users_info, user, redis)
    return {
        info[b'uid']: {
            'distance': distances[info[b'uid']],
            **info,
        } for info in users_info if info[b'uid'] != user.encode()
    }


async def get_users_distances(users_info, user, redis):
    _map = await _create_map(users_info, user, redis)
    result = await redis.georadiusbymember(_map, user, 10, unit='km', with_dist=True)
    await redis.delete(_map)
    return {geo.member: geo.dist for geo in result}


async def _create_map(users_data, user, redis):
    key = f'map:user:{user}'
    await asyncio.gather(
        *[redis.geoadd(key, data[b'longitude'], data[b'latitude'], data[b'uid']) for data in users_data],
        return_exceptions=True
    )
    return key
