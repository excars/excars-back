from starlette.requests import Request


def get_redis_cli(request: Request):
    return request.app.redis_cli
