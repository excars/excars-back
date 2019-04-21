import os

GOOGLE_OAUTH2_CLIENT_ID = os.getenv("GOOGLE_OAUTH2_CLIENT_ID")

REDIS_HOST = os.getenv("REDIS_HOST", "redis://redis")
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_POOL_MIN = int(os.getenv("REDIS_POOL_MIN", "0"))
REDIS_POOL_MAX = int(os.getenv("REDIS_POOL_MAX", "10"))

_MIN = 60

RIDE_REQUEST_TTL = 5 * _MIN
RIDE_TTL = 60 * _MIN

PUBLISH_MAP_FREQUENCY = 1
