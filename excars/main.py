from fastapi import FastAPI

from excars import api, oauth2_redirect

app = FastAPI(debug=True)
app.include_router(api.v1.router, prefix="/api/v1")
app.include_router(oauth2_redirect.router)
