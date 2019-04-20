from aioredis import Redis
from fastapi import APIRouter, Depends, HTTPException

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
    Sets role and destination for current user
    """
    profile = Profile.from_user(user, role=join_request.role, destination=join_request.destination)
    await repositories.profile.save(redis_cli, profile)
    return profile


@router.get("/profiles/{profile_id}", tags=["profiles"], response_model=Profile)
async def get_profile(profile_id: int, redis_cli: Redis = Depends(get_redis_cli)):
    """
    Gets profile
    """
    profile = await repositories.profile.get(redis_cli, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")
    return profile
