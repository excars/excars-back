from pydantic import BaseModel


class User(BaseModel):
    user_id: int
    email: str
    name: str
    first_name: str
    last_name: str
    avatar: str
