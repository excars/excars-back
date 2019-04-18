from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Role(str, Enum):
    driver = "driver"
    hitchhiker = "hitchhiker"


class Destination(BaseModel):
    name: str
    latitude: Decimal
    longitude: Decimal


class JoinRequest(BaseModel):
    role: Role
    destination: Destination


class Profile(BaseModel):
    user_id: str
    name: str
    avatar: str
    role: Optional[Role]
    destination: Optional[Destination]
