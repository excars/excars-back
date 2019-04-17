from pydantic import BaseModel


class TokenPayload(BaseModel):
    sub: str
    email: str
    name: str
    family_name: str
    given_name: str
    picture: str
