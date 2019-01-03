import os

from ._env import get_bool

APP_DEBUG = get_bool('DEBUG')
APP_HOST = os.getenv('APP_HOST', '0.0.0.0')
APP_PORT = int(os.getenv('APP_PORT', '8000'))
APP_WORKERS = int(os.getenv('APP_WORKERS', '1'))

WEBSOCKET_MAX_SIZE = 2 ** 20
WEBSOCKET_MAX_QUEUE = 32
WEBSOCKET_READ_LIMIT = 2 ** 16
WEBSOCKET_WRITE_LIMIT = 2 ** 16


APP_MODELS = (
    'excars.auth.models.User',
)


_MIN = 60

RIDE_REQUEST_TTL = 30
RIDE_TTL = 60 * _MIN
PROFILE_TTL_ON_CLOSE = 5 * _MIN
LOCATION_TTL = 5 * _MIN

PUBLISH_MAP_FREQUENCY = 1
READ_STREAM_FREQUENCY = 1