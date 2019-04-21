from fastapi import APIRouter

from . import profiles, rides, users, ws

router = APIRouter()
router.include_router(profiles.router)
router.include_router(rides.router, tags=["rides"])
router.include_router(users.router)
router.include_router(ws.router)
