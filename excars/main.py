from fastapi import FastAPI

from excars import api

app = FastAPI()
app.include_router(api.v1.router, prefix="/api/v1")
