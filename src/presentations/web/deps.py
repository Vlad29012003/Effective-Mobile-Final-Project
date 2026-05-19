from starlette.requests import Request

from configs import settings as _settings
from packages.security.jwt import JwtConfig, JwtManager, JwtTokenPayload

_jwt = JwtManager(
    JwtConfig(
        secret_key=_settings.JWT_SECRET_KEY,
        algorithm=_settings.JWT_ALGORITHM,
        issuer=_settings.JWT_ISSUER,
        audience=_settings.JWT_AUDIENCE,
        leeway_seconds=_settings.JWT_LEEWAY_SECONDS,
    )
)


def get_web_user(request: Request) -> JwtTokenPayload | None:
    token = request.cookies.get(_settings.AUTH_ACCESS_COOKIE_NAME)
    if not token:
        return None
    try:
        return _jwt.decode(token)
    except Exception:
        return None
