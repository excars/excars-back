USER_PREFIX = "user:"
STREAM_PREFIX = "stream:"


def get_user_info_redis_key(user):
    return f"{USER_PREFIX}{user}"


def get_user_stream(user):
    return f"{STREAM_PREFIX}{user}"
