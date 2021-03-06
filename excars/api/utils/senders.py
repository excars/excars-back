import asyncio
from typing import Awaitable, List

from aioredis import Redis
from starlette.websockets import WebSocket, WebSocketState

from excars import config, repositories
from excars.models.locations import MapItem, UserLocation
from excars.models.messages import Message, MessageType
from excars.models.user import User


def send(websocket: WebSocket, user: User, redis_cli: Redis) -> List[Awaitable]:
    return [publish_map(websocket, user, redis_cli)]


async def publish_map(websocket: WebSocket, user: User, redis_cli: Redis) -> None:
    while websocket.application_state == WebSocketState.CONNECTED:
        locations = await repositories.locations.list_for(redis_cli, user_id=user.user_id)
        map_items = await _prepare_map(user.user_id, locations, redis_cli)
        message = Message(type=MessageType.map, data=map_items)
        await websocket.send_text(message.json())
        await asyncio.sleep(config.PUBLISH_MAP_FREQUENCY)


async def _prepare_map(user_id: str, locations: List[UserLocation], redis_cli: Redis) -> List[MapItem]:
    user_ride_id = await repositories.rides.get_ride_id(redis_cli, user_id)

    map_items = []
    for location in locations:
        if location.user_id == user_id:
            continue

        profile = await repositories.profile.get(redis_cli, location.user_id)
        if not profile:
            continue

        ride_id = await repositories.rides.get_ride_id(redis_cli, profile.user_id)
        if ride_id and ride_id != user_ride_id:
            continue

        map_items.append(
            MapItem(
                user_id=profile.user_id,
                role=profile.role,
                location=location,
                has_same_ride=bool(user_ride_id and (user_ride_id == ride_id)),
            )
        )

    return map_items
