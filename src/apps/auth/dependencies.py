from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from configs import settings as _settings
from packages.security.jwt import JwtConfig, JwtManager, JwtTokenPayload

bearer_scheme = HTTPBearer(auto_error=False)

# APP-scoped singleton, built once from the settings singleton
_jwt_manager = JwtManager(
    JwtConfig(
        secret_key=_settings.JWT_SECRET_KEY,
        algorithm=_settings.JWT_ALGORITHM,
        issuer=_settings.JWT_ISSUER,
        audience=_settings.JWT_AUDIENCE,
        leeway_seconds=_settings.JWT_LEEWAY_SECONDS,
    )
)


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)] = None,
) -> JwtTokenPayload:
    token: str | None = credentials.credentials if credentials else None
    if not token:
        token = request.cookies.get(_settings.AUTH_ACCESS_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return _jwt_manager.decode(token)
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail="Token has expired") from e
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail="Invalid token") from e


CurrentUser = Annotated[JwtTokenPayload, Depends(get_current_user)]
