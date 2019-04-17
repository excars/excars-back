from fastapi import APIRouter

router = APIRouter()


@router.get("/join")
def join():
    return {"message": "Hello World"}
