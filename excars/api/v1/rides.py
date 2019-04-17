from fastapi import APIRouter, Depends

from excars.api.utils.security import get_current_user
from excars.models.rides import JoinRequest, Profile
from excars.models.user import User

router = APIRouter()


@router.post("/join", tags=["rides"], response_model=Profile)
def join(*, join_request: JoinRequest, user: User = Depends(get_current_user)):
    """
    Sets role for current user
    """
    return Profile(
        user_id=user.user_id,
        name=user.name,
        avatar=user.avatar,
        role=join_request.role,
        destination=join_request.destination,
    )
