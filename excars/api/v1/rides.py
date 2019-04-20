from aioredis import Redis
from fastapi import APIRouter, Depends, HTTPException

from excars import repositories
from excars.api.utils.redis import get_redis_cli
from excars.api.utils.security import get_current_user
from excars.models.profiles import Profile, Role
from excars.models.rides import RideRequest, RideRequestCreate, RideRequestStatus, RideRequestUpdate
from excars.models.user import User

router = APIRouter()


@router.post("/rides", response_model=RideRequest)
async def create_ride_request(
    ride_create: RideRequestCreate, user: User = Depends(get_current_user), redis_cli: Redis = Depends(get_redis_cli)
):
    """
    Creates request for a ride
    """
    receiver = await repositories.profile.get(redis_cli, ride_create.receiver)
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found.")

    sender = await repositories.profile.get(redis_cli, user.user_id)
    if not sender:
        sender = Profile.from_user(user, role=Role.opposite(receiver.role), destination=receiver.destination)
        await repositories.profile.save(redis_cli, sender)

    ride_request = RideRequest(sender=sender, receiver=receiver, status=RideRequestStatus.requested)
    await repositories.rides.create_request(redis_cli, ride_request)

    return ride_request


@router.delete("/rides", status_code=204)
async def leave_ride(user: User = Depends(get_current_user), redis_cli: Redis = Depends(get_redis_cli)):
    """
    Remove current user from ride
    """
    profile = await repositories.profile.get(redis_cli, user.user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")
    await repositories.rides.delete_or_exclude(redis_cli, profile)
    return {}


@router.put("/rides/{ride_id}", response_model=RideRequest)
async def update_ride_request(
    ride_id: int,
    ride_update: RideRequestUpdate,
    user: User = Depends(get_current_user),
    redis_cli: Redis = Depends(get_redis_cli),
):
    """
    Updates ride request status
    """
    receiver = await repositories.profile.get(redis_cli, user.user_id)
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found.")

    sender = await repositories.profile.get(redis_cli, ride_update.passenger_id or ride_id)
    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found.")

    ride_request = RideRequest(sender=sender, receiver=receiver, status=ride_update.status)
    if not await repositories.rides.request_exists(redis_cli, ride_request):
        raise HTTPException(status_code=404, detail="Ride request not found.")

    await repositories.rides.update_request(redis_cli, ride_request)

    return ride_request
