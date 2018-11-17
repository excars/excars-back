import datetime

from .. import event
from ..utils import get_user_info_redis_key

USER_INFO_TTL = 60 * 30


@event.listen('LOCATION')
async def handler(request, data):
    await process_location(data, request['user'], request.app.redis)


async def process_location(data, user_uid, redis):
    data = {**data, 'last': datetime.datetime.utcnow().timestamp()}
    redis_key = get_user_info_redis_key(user_uid)

    await redis.hmset_dict(redis_key, data)
    if not await redis.hexists(redis_key, 'uid'):
        await redis.hmset_dict(redis_key, _get_user_info(user_uid))
        await redis.expire(redis_key, USER_INFO_TTL)


def _get_user_info(user):
    return {'uid': user}
