import asyncio
from asyncio import Task
from typing import List, Optional

from aioredis import Redis
from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket

from excars import config, repositories
from excars.api.utils import receivers, senders
from excars.api.utils.security import get_current_user
from excars.models.messages import Message, MessageType
from excars.models.user import User

router = APIRouter()


@router.websocket_route("/ws")
class Stream(WebSocketEndpoint):
    encoding = "json"
    tasks: Optional[List[Task]] = None
    user: Optional[User] = None
    redis_cli: Redis

    async def on_connect(self, websocket: WebSocket) -> None:
        self.redis_cli = websocket.app.redis_cli
        await websocket.accept()
        try:
            self.user = get_current_user(token=websocket.headers.get("Authorization", ""))
        except HTTPException:
            await websocket.close()
        else:
            self.tasks = senders.init(websocket, self.user, self.redis_cli)
            asyncio.create_task(repositories.profile.persist(self.redis_cli, self.user.user_id))
            asyncio.create_task(repositories.rides.persist(self.redis_cli, self.user.user_id))

    async def on_receive(self, websocket: WebSocket, data) -> None:
        try:
            message = Message(**data)
            await receivers.handle(message, self.user, self.redis_cli)
        except ValidationError as exc:
            await websocket.send_text(Message(type=MessageType.error, data=exc.errors()).json())

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        if self.tasks is not None:
            [task.cancel() for task in self.tasks]  # pylint: disable=expression-not-assigned

        if self.user is not None:
            profile = await repositories.profile.get(self.redis_cli, self.user.user_id)
            asyncio.create_task(repositories.profile.expire(self.redis_cli, self.user.user_id))
            asyncio.create_task(repositories.rides.delete_or_exclude(self.redis_cli, profile, config.PROFILE_TTL))

        await super().on_disconnect(websocket, close_code)
