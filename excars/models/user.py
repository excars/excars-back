from pydantic import BaseModel


class User(BaseModel):
    user_id: str
    email: str
    name: str
    first_name: str
    last_name: str
    avatar: str
