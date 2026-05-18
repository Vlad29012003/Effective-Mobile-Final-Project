from typing import Annotated

import jwt
from dishka.integrations.fastapi import FromDishka
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from configs.settings import Settings
from packages.security.jwt import JwtManager, JwtTokenPayload

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    jwt_manager: FromDishka[JwtManager],
    settings: FromDishka[Settings],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)] = None,
) -> JwtTokenPayload:
    token: str | None = None
    if credentials:
        token = credentials.credentials
    if not token:
        token = request.cookies.get(settings.AUTH_ACCESS_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return jwt_manager.decode(token)
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail="Token has expired") from e
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail="Invalid token") from e


CurrentUser = Annotated[JwtTokenPayload, Depends(get_current_user)]
