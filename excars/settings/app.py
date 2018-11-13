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
