

USER_PREFIX = 'user:'


def get_user_info_redis_key(user):
    return f'{USER_PREFIX}{user}'
