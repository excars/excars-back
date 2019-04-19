from fastapi import APIRouter

from . import profiles, rides, users

router = APIRouter()
router.include_router(profiles.router)
router.include_router(rides.router, tags=["rides"])
router.include_router(users.router)
