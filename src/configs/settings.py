import json
import os
from typing import Any
from urllib.parse import quote_plus

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict


def split_comma_separated(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, str):
        items = value.split(",")
    elif isinstance(value, (list | tuple | set)):
        items = [str(item) for item in value]
    else:
        items = [str(value)]
    return [item.strip() for item in items if item and item.strip()]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
        secrets_dir=["/run/secrets", "/etc/secrets"],
        env_file=".env",
        env_file_encoding="utf-8",
    )

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if self.APP_ENV == "production" and "DOCS_ENABLED" not in os.environ:
            self.DOCS_ENABLED = False
        if self.APP_ENV != "local" and "LOG_FORMAT" not in os.environ:
            self.LOG_FORMAT = "json"

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # Priority: constructor > secrets > env > .env
        return (
            init_settings, # argements constructor 
            file_secret_settings, # Dcker secrets
            env_settings, # environment variables
            dotenv_settings, # .env file
        )

    # -------------------------------------------------------------------------
    # Core
    # -------------------------------------------------------------------------
    APP_NAME: str = "final-project"
    APP_ENV: str = "local"  # local | development | staging | production
    APP_VERSION: str | None = None
    DEBUG: bool = True
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "text"

    # API docs (Swagger / ReDoc) — disabled automatically in prod
    DOCS_ENABLED: bool = True
    DOCS_URL: str | None = "/docs"
    REDOC_URL: str | None = "/redoc"

    # SQLAdmin mount path
    ADMIN_BASE_PATH: str = "/admin"

    # -------------------------------------------------------------------------
    # Database
    # -------------------------------------------------------------------------
    DB_DRIVER: str = "postgresql+asyncpg"
    DB_HOST: str | None = None
    DB_PORT: int | None = None
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DB_NAME: str | None = None
    DB_OPTIONS: str | None = None

    DB_POOL_SIZE: int | None = None
    DB_MAX_OVERFLOW: int | None = None

    # Direct URL overrides (takes priority over DB_* components)
    DATABASE_URL: str | None = None
    SYNC_DATABASE_URL: str | None = None
    SYNC_DB_DRIVER: str | None = None

    def build_database_url(self) -> str | None:
        if not all([self.DB_HOST, self.DB_USER, self.DB_PASSWORD, self.DB_NAME, self.DB_PORT]):
            return None
        safe_user = quote_plus(self.DB_USER or "")
        safe_pass = quote_plus(self.DB_PASSWORD or "")
        base = (
            f"{self.DB_DRIVER}://{safe_user}:{safe_pass}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
        if self.DB_OPTIONS:
            sep = "?" if "?" not in base else "&"
            return f"{base}{sep}{self.DB_OPTIONS}"
        return base

    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return self.build_database_url() or ""

    def get_sync_database_url(self) -> str:
        if self.SYNC_DATABASE_URL:
            return self.SYNC_DATABASE_URL
        if self.SYNC_DB_DRIVER:
            return self._build_sync_url(self.SYNC_DB_DRIVER) or ""
        return ""

    def _build_sync_url(self, driver: str) -> str | None:
        if not all([self.DB_HOST, self.DB_USER, self.DB_PASSWORD, self.DB_NAME, self.DB_PORT]):
            return None
        safe_user = quote_plus(self.DB_USER or "")
        safe_pass = quote_plus(self.DB_PASSWORD or "")
        base = f"{driver}://{safe_user}:{safe_pass}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        if self.DB_OPTIONS:
            sep = "?" if "?" not in base else "&"
            return f"{base}{sep}{self.DB_OPTIONS}"
        return base

    # -------------------------------------------------------------------------
    # Auth / JWT
    # -------------------------------------------------------------------------
    JWT_SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRES_DAYS: int = 30
    JWT_ISSUER: str | None = None
    JWT_AUDIENCE: str | None = None
    JWT_LEEWAY_SECONDS: int = 30

    # Sessions (for Admin login form) — falls back to JWT_SECRET_KEY if not set
    SESSION_SECRET_KEY: str | None = None

    # Cookies
    COOKIE_SECURE: bool = True
    COOKIE_SAMESITE: str = "Lax"
    COOKIE_DOMAIN: str | None = None

    AUTH_ACCESS_COOKIE_NAME: str = "auth_access_token"
    AUTH_REFRESH_COOKIE_NAME: str = "auth_refresh_token"
    AUTH_ACCESS_COOKIE_PATH: str = "/"
    AUTH_REFRESH_COOKIE_PATH: str = "/api/v1/auth/refresh"

    def get_auth_cookie_params(self) -> dict[str, str | bool | None]:
        return {
            "secure": self.COOKIE_SECURE,
            "samesite": self.COOKIE_SAMESITE,
            "domain": self.COOKIE_DOMAIN,
        }

    # -------------------------------------------------------------------------
    # CORS
    # -------------------------------------------------------------------------
    CORS_ORIGINS: list[str] = Field(default_factory=list)

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _parse_cors(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            s = value.strip()
            if s.startswith("[") and s.endswith("]"):
                try:
                    parsed = json.loads(s)
                except json.JSONDecodeError:
                    parsed = None
                if isinstance(parsed, list):
                    return [str(x).strip() for x in parsed if str(x).strip()]
        return split_comma_separated(value)

    # -------------------------------------------------------------------------
    # Redis
    # -------------------------------------------------------------------------
    REDIS_URL: str | None = None

    # -------------------------------------------------------------------------
    # Pagination
    # -------------------------------------------------------------------------
    PAGINATION_DEFAULT_PAGE: int = 1
    PAGINATION_DEFAULT_PAGE_SIZE: int = 20
    PAGINATION_MAX_PAGE_SIZE: int = 100

    # -------------------------------------------------------------------------
    # Observability / Sentry
    # -------------------------------------------------------------------------
    SENTRY_ENABLED: bool = False
    SENTRY_DSN: str | None = None
    SENTRY_ENV: str | None = None  # defaults to APP_ENV if not set
    SENTRY_RELEASE: str | None = None
    SENTRY_TRACES_SAMPLE_RATE: float = 0.0
    SENTRY_PROFILES_SAMPLE_RATE: float = 0.0
    SENTRY_SEND_PII: bool = False
