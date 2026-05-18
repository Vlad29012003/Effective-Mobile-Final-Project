from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from packages.security.jwt import JwtManager, JwtTokenPayload

bearer_scheme = HTTPBearer(auto_error=False)


def _extract_token(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    cookie_name: str,
) -> str | None:
    if credentials:
        return credentials.credentials
    return request.cookies.get(cookie_name)


def get_current_user(
    jwt_manager: JwtManager,
    token: str,
) -> JwtTokenPayload:
    """Decode and validate a JWT token, raising 401 on any error."""
    try:
        return jwt_manager.decode(token)
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail="Token has expired") from e
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail="Invalid token") from e
