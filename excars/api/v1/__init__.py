from fastapi import APIRouter

from . import rides

router = APIRouter()
router.include_router(rides.router)
