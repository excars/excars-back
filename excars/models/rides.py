from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class Destination(BaseModel):
    name: str
    latitude: Decimal
    longitude: Decimal


class JoinRequest(BaseModel):
    role: str
    destination: Destination


class Profile(BaseModel):
    user_id: str
    name: str
    avatar: str
    role: Optional[str]
    destination: Optional[Destination]
