from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from .profiles import Role


class Location(BaseModel):
    latitude: Decimal
    longitude: Decimal
    course: Decimal


class UserLocation(BaseModel):
    user_id: str
    latitude: Decimal
    longitude: Decimal
    course: Decimal
    ts: float


class MapItem(BaseModel):
    user_id: str
    role: Optional[Role]
    location: UserLocation
    has_same_ride: bool
