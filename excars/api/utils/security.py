from aioredis import Redis
from fastapi import Depends, HTTPException, Security
from fastapi.openapi.models import OAuthFlowAuthorizationCode, OAuthFlows
from fastapi.security import OAuth2
from google.auth.transport.requests import Request
from google.oauth2.id_token import verify_oauth2_token
from pydantic import ValidationError
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from excars import config, repositories
from excars.api.utils.redis import get_redis_cli
from excars.models.token import TokenPayload
from excars.models.user import User

oauth2 = OAuth2(  # pylint: disable=invalid-name
    flows=OAuthFlows(
        authorizationCode=OAuthFlowAuthorizationCode(
            authorizationUrl="https://accounts.google.com/o/oauth2/v2/auth?scope=openid+email+profile",
            tokenUrl="https://oauth2.googleapis.com/token",
        )
    )
)

request = Request()  # pylint: disable=invalid-name


async def get_current_user(token: str = Security(oauth2), redis_cli: Redis = Depends(get_redis_cli)) -> User:
    try:
        payload = verify_oauth2_token(token.rpartition(" ")[-1], Request(), config.GOOGLE_OAUTH2_CLIENT_ID)
    except ValueError as exc:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    if payload["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Wrong issuer.")

    try:
        token_data = TokenPayload(**payload)
    except ValidationError as exc:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=exc.json(indent=None)) from exc

    user = await repositories.users.get(redis_cli, user_id=token_data.sub)
    if user is None:
        user = User.from_token(token_data)
        await repositories.users.save(redis_cli, user)
    return user
