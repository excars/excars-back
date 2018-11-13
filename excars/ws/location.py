import datetime
import asyncio

import ujson
from sanic import Blueprint

bp = Blueprint('ws_location')
USER_INFO_TTL = 60 * 30
USER_PREFIX = 'user:'
PUB_LOCATION_FREQUENCY = 5


@bp.websocket('/location')
async def geo_chanel(request, ws):
    await asyncio.gather(publish_location(request, ws), subscribe_map(request, ws))


async def publish_location(request, ws):
    while True:
        try:
            data = ujson.loads(await ws.recv())
        except ValueError:
            continue
        await process_location(data, request['user'], request.app.redis)


async def process_location(data, user_uid, redis):
    data = {**data, 'last': datetime.datetime.utcnow().timestamp()}
    redis_key = _get_user_info_redis_key(user_uid)

    await redis.hmset_dict(redis_key, data)
    if not await redis.hexists(redis_key, 'uid'):
        await redis.hmset_dict(redis_key, _get_user_info(user_uid))
        await redis.expire(redis_key, USER_INFO_TTL)


async def subscribe_map(request, ws):
    while True:
        await ws.send(ujson.dumps(await _get_users_data(request['user'], request.app.redis)))
        await asyncio.sleep(PUB_LOCATION_FREQUENCY)


async def _get_users_data(user, redis):
    users_info = await asyncio.gather(
        *[redis.hgetall(k) async for k in get_all_keys(USER_PREFIX, redis)],
        return_exceptions=True
    )
    distances = await _get_users_distances(users_info, user, redis)
    return {
        info['uid']: {
            'distance': distances[info['uid']],
            **info,
        } for info in users_info
    }


async def _get_users_distances(users_info, user, redis):
    map = await create_map(users_info, user, redis)
    result = await redis.georadiusbymember(map, user, 10, unit='km', with_dist=True)
    await redis.delete(map)
    return {geo.member: geo.dist for geo in result}


async def create_map(users_data, user, redis):
    key = f'map:user:{user}'
    print(users_data)
    await asyncio.gather(
        *[redis.geoadd(key, data[b'longitude'], data[b'latitude'], data[b'uid']) for data in users_data],
        return_exceptions=True
    )
    return key


async def get_all_keys(prefix, redis):
    cur = b'0'  # set initial cursor to 0
    while cur:
        cur, keys = await redis.scan(cur, match=f'{prefix}*')
        for key in keys:
            yield key


def _get_user_info(user):
    return {'uid': user}


def _get_user_info_redis_key(user):
    return f'{USER_PREFIX}{user}'
