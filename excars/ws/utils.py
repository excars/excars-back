

USER_PREFIX = 'user:'


def get_user_info_redis_key(user):
    return f'{USER_PREFIX}{user}'


async def get_all_keys(prefix, redis):
    cur = b'0'  # set initial cursor to 0
    while cur:
        cur, keys = await redis.scan(cur, match=f'{prefix}*')
        for key in keys:
            yield key
