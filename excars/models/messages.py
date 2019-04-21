from enum import Enum

from pydantic import BaseModel, Json


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


class Message(BaseModel):
    type: MessageType
    data: Json
