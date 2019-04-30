from enum import Enum
from typing import Any, Dict, NamedTuple

from pydantic import BaseModel


class MessageType(str, Enum):
    location = "LOCATION"
    map = "MAP"
    ride_requested = "RIDE_REQUESTED"
    ride_request_accepted = "RIDE_REQUEST_ACCEPTED"
    ride_request_declined = "RIDE_REQUEST_DECLINED"
    ride_updated = "RIDE_UPDATED"
    ride_cancelled = "RIDE_CANCELLED"

    socket_close = "_WEBSOCKET_CLOSE"
    socket_open = "_WEBSOCKET_OPEN"

    error = "ERROR"


class Message(BaseModel):
    type: MessageType
    data: Any


class StreamMessage(NamedTuple):
    stream: str
    message_id: int
    data: Dict[bytes, Any]
