import ujson

from .. import event


@event.stream_handler('USER_CONNECT')
async def user_connect(request, ws, message, user):
    del request, message, user
    await ws.send(ujson.dumps({'type': 'CHECK', 'connected': True}))
