from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from .profiles import Role


class UserLocation(BaseModel):
    user_id: int
    latitude: Decimal
    longitude: Decimal
    course: Decimal
    ts: float


class MapItem(BaseModel):
    user_id: int
    role: Optional[Role]
    location: UserLocation
    has_same_ride: bool
