import sentry_sdk
from sentry_sdk.integrations.sanic import SanicIntegration

from .settings import logging as logging_settings


def setup(app, _):
    del app
    if logging_settings.SENTRY_DSN:
        sentry_sdk.init(dsn=logging_settings.SENTRY_DSN, integrations=[SanicIntegration()])
