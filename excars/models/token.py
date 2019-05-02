from typing import Optional

from pydantic import BaseModel


class TokenPayload(BaseModel):
    sub: str
    email: str
    name: Optional[str]
    family_name: Optional[str]
    given_name: Optional[str]
    picture: Optional[str]
