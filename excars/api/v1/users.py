from fastapi import APIRouter, Depends

from excars.api.utils.security import get_current_user
from excars.models.user import User

router = APIRouter()


@router.get("/users/me", response_model=User)
async def retrieve_me(user: User = Depends(get_current_user)):
    """
    Gets current user
    """
    return user
