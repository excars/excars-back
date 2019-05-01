import asyncio

from fastapi import APIRouter, HTTPException
from starlette.websockets import WebSocket, WebSocketDisconnect

from excars import config, repositories
from excars.api.utils import receivers, senders, stream
from excars.api.utils.security import get_current_user

router = APIRouter()


@router.websocket_route("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    redis_cli = websocket.app.redis_cli
    try:
        user = await get_current_user(websocket.headers.get("Authorization", ""), redis_cli=redis_cli)
    except HTTPException:
        await websocket.close()
        return

    await asyncio.gather(
        repositories.profile.persist(redis_cli, user.user_id), repositories.rides.persist(redis_cli, user.user_id)
    )

    try:
        await asyncio.gather(
            receivers.init(websocket, user, redis_cli),
            stream.init(websocket, user, redis_cli),
            *senders.init(websocket, user, redis_cli),
        )
    except WebSocketDisconnect:
        pass
    finally:
        await repositories.profile.expire(redis_cli, user.user_id)
        profile = await repositories.profile.get(redis_cli, user.user_id)
        if profile is not None:
            await repositories.rides.delete_or_exclude(redis_cli, profile, config.PROFILE_TTL)
        await websocket.close()
