import os

REDIS_URL = os.getenv('REDIS_URL', 'redis://redis')
REDIS_DB = int(os.getenv('REDIS_DB', '0'))

REDIS_POOL_MIN = int(os.getenv('REDIS_POOL_MIN', '0'))
REDIS_POOL_MAX = int(os.getenv('REDIS_POOL_MAX', '10'))
