from fastapi import APIRouter

from . import profiles, users

router = APIRouter()
router.include_router(profiles.router)
router.include_router(users.router)
