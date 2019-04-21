import asyncio
from asyncio import Task
from typing import List

from fastapi import APIRouter, HTTPException
from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket

from excars.api.utils import senders
from excars.api.utils.security import get_current_user

router = APIRouter()


@router.websocket_route("/ws")
class Stream(WebSocketEndpoint):
    encoding = "json"
    tasks: List[Task]

    async def on_connect(self, websocket) -> None:
        try:
            user = get_current_user(token=websocket.headers.get("Authorization", ""))
        except HTTPException:
            await websocket.close()
        else:
            await websocket.accept()
            redis_cli = websocket.app.redis_cli
            self.tasks = senders.init(websocket, user, redis_cli)

    async def on_receive(self, websocket, data):
        await asyncio.sleep(5)

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        [task.cancel() for task in self.tasks]  # pylint: disable=expression-not-assigned
        await super().on_disconnect(websocket, close_code)
