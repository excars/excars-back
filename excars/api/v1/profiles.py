from aioredis import Redis
from fastapi import APIRouter, Depends

from excars import repositories
from excars.api.utils.redis import get_redis_cli
from excars.api.utils.security import get_current_user
from excars.models.profiles import JoinRequest, Profile
from excars.models.user import User

router = APIRouter()


@router.post("/profiles", tags=["profiles"], response_model=Profile)
async def join(
    *, join_request: JoinRequest, user: User = Depends(get_current_user), redis_cli: Redis = Depends(get_redis_cli)
):
    """
    Sets role for current user
    """
    profile = Profile(
        user_id=user.user_id,
        name=user.name,
        avatar=user.avatar,
        role=join_request.role,
        destination=join_request.destination,
    )

    await repositories.profile.save(redis_cli, profile)

    return profile
