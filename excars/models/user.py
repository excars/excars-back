from pydantic import BaseModel

from excars.models.token import TokenPayload


class User(BaseModel):
    user_id: int
    email: str
    name: str
    first_name: str
    last_name: str
    avatar: str

    @classmethod
    def from_token(cls, token: TokenPayload) -> "User":
        return cls(
            user_id=token.sub,
            email=token.email,
            name=token.name,
            first_name=token.family_name,
            last_name=token.given_name,
            avatar=token.picture,
        )
