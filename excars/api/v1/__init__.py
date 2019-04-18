from fastapi import APIRouter

from . import rides, users

router = APIRouter()
router.include_router(rides.router)
router.include_router(users.router)
