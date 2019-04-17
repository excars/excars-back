from fastapi import HTTPException, Security
from fastapi.openapi.models import OAuthFlowAuthorizationCode, OAuthFlows
from fastapi.security import OAuth2
from google.auth.transport.requests import Request
from google.oauth2.id_token import verify_oauth2_token
from pydantic import ValidationError
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from excars import config
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


def get_current_user(token: str = Security(oauth2)):
    try:
        payload = verify_oauth2_token(token.rpartition(" ")[-1], Request(), config.GOOGLE_OAUTH2_CLIENT_ID)
    except ValueError:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Token expired.")
    if payload["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Wrong issuer.")
    try:
        token_data = TokenPayload(**payload)
    except ValidationError as exc:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=exc.json(indent=None)) from exc
    return User(
        user_id=token_data.sub,
        email=token_data.email,
        name=token_data.name,
        first_name=token_data.family_name,
        last_name=token_data.given_name,
        avatar=token_data.picture,
    )
