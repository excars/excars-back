import os


def get_bool(key: str) -> bool:
    value = os.getenv(key)
    if value:
        return value.lower() in ["true", "1", "t"]
    return False


DEBUG = get_bool("APP_DEBUG")

GOOGLE_OAUTH2_CLIENT_ID = os.getenv("GOOGLE_OAUTH2_CLIENT_ID")

REDIS_HOST = os.getenv("REDIS_HOST", "redis://redis")
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_POOL_MIN = int(os.getenv("REDIS_POOL_MIN", "0"))
REDIS_POOL_MAX = int(os.getenv("REDIS_POOL_MAX", "10"))

_MIN = 60

RIDE_REQUEST_TTL = 5 * _MIN
RIDE_TTL = 60 * _MIN
PROFILE_TTL = 15 * _MIN

PUBLISH_MAP_FREQUENCY = 1
READ_STREAM_FREQUENCY = 1
