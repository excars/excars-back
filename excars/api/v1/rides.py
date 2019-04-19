from aioredis import Redis
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from excars import repositories
from excars.api.utils.redis import get_redis_cli
from excars.api.utils.security import get_current_user
from excars.models.profiles import Profile, Role
from excars.models.rides import RideRequest, RideRequestStatus
from excars.models.user import User

router = APIRouter()


class RideRequestIn(BaseModel):
    receiver: int


@router.post("/rides", response_model=RideRequest)
async def create_ride_request(
    request_in: RideRequestIn, user: User = Depends(get_current_user), redis_cli: Redis = Depends(get_redis_cli)
):
    receiver = await repositories.profile.get(redis_cli, request_in.receiver)
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found.")

    sender = await repositories.profile.get(redis_cli, int(user.user_id))
    if not sender:
        await repositories.profile.save(
            redis_cli,
            Profile(
                user_id=user.user_id,
                name=user.name,
                avatar=user.avatar,
                role=Role.opposite(receiver.role),
                destination=receiver.destination,
            ),
        )

    ride_request = RideRequest(sender=sender, receiver=receiver, status=RideRequestStatus.requested)
    await repositories.rides.create_request(redis_cli, ride_request)

    return ride_request
