from asyncio import Task
from typing import List

from aioredis import Redis
from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket

from excars.api.utils import receivers, senders
from excars.api.utils.security import get_current_user
from excars.models.messages import Message
from excars.models.user import User

router = APIRouter()


@router.websocket_route("/ws")
class Stream(WebSocketEndpoint):
    encoding = "json"
    tasks: List[Task]
    user: User
    redis_cli: Redis

    async def on_connect(self, websocket) -> None:
        try:
            self.user = get_current_user(token=websocket.headers.get("Authorization", ""))
        except HTTPException:
            await websocket.close()
        else:
            await websocket.accept()
            self.redis_cli = websocket.app.redis_cli
            self.tasks = senders.init(websocket, self.user, self.redis_cli)

    async def on_receive(self, websocket: WebSocket, data) -> None:
        try:
            message = Message(**data)
        except ValidationError as exc:
            await websocket.send_json(exc.json())
        else:
            await receivers.handle(message, self.user, self.redis_cli)

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        [task.cancel() for task in self.tasks]  # pylint: disable=expression-not-assigned
        await super().on_disconnect(websocket, close_code)
