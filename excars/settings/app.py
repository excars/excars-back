import os

from ._env import get_bool

APP_DEBUG = get_bool('DEBUG')
APP_HOST = os.getenv('APP_HOST', '0.0.0.0')
APP_PORT = int(os.getenv('APP_PORT', '8000'))
APP_WORKERS = int(os.getenv('APP_WORKERS', '1'))
