from __future__ import annotations

import datetime as dt

from dishka import Provider, Scope, provide

from configs import Settings
from packages.security import PasswordHasher
from packages.security.jwt import JwtConfig, JwtManager


class SecurityProvider(Provider):
    @provide(scope=Scope.APP)
    def password_hasher(self) -> PasswordHasher:
        return PasswordHasher()

    @provide(scope=Scope.APP)
    def jwt_manager(self, settings: Settings) -> JwtManager:
        cfg = JwtConfig(
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
            leeway_seconds=settings.JWT_LEEWAY_SECONDS,
        )
        return JwtManager(cfg)

    @provide(scope=Scope.APP)
    def access_ttl(self, settings: Settings) -> dt.timedelta:
        return dt.timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRES_MINUTES)

    @provide(scope=Scope.APP)
    def refresh_ttl(self, settings: Settings) -> dt.timedelta:
        return dt.timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRES_DAYS)
