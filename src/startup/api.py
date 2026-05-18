from dishka import AsyncContainer
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from configs import settings
from di import ConfigProvider, DBProvider, PaginationProvider, RedisProvider, SecurityProvider
from di.container import build_container, setup_di
from framework.apps import AppRegistry
from framework.discovery import discover_app_paths, load_app_configs
from packages.logging import configure_logging
from presentations.api.exception_handlers import get_exception_handlers
from presentations.api.middlewares.trace import TraceIdMiddleware


def create_app(container: AsyncContainer | None = None) -> FastAPI:
    # ── 1. Logging ────────────────────────────────────────────────────────────
    configure_logging(settings.LOG_LEVEL, settings.LOG_FORMAT, debug=settings.DEBUG)

    # ── 2. Sentry ─────────────────────────────────────────────────────────────
    if settings.SENTRY_ENABLED and settings.SENTRY_DSN:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENV or settings.APP_ENV,
            release=settings.SENTRY_RELEASE,
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE,
            send_default_pii=settings.SENTRY_SEND_PII,
            integrations=[FastApiIntegration(), SqlalchemyIntegration()],
        )

    # ── 3. Discover apps and collect components ───────────────────────────────
    app_registry = AppRegistry()
    app_paths = discover_app_paths()
    app_configs = load_app_configs(app_paths)
    for app_config in app_configs:
        app_config.install(app_registry)

    # ── 4. Build DI container ─────────────────────────────────────────────────
    if container is None:
        infrastructure_providers = [
            ConfigProvider(),
            DBProvider(),
            SecurityProvider(),
            RedisProvider(),
            PaginationProvider(),
        ]
        container = build_container(infrastructure_providers + app_registry.get_all_providers())

    # ── 5. Create FastAPI app ─────────────────────────────────────────────────
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION or "0.1.0",
        docs_url=settings.DOCS_URL if settings.DOCS_ENABLED else None,
        redoc_url=settings.REDOC_URL if settings.DOCS_ENABLED else None,
    )

    # ── 6. Middlewares ────────────────────────────────────────────────────────
    cors_origins = settings.CORS_ORIGINS or [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TraceIdMiddleware)
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SESSION_SECRET_KEY or settings.JWT_SECRET_KEY,
    )

    # ── 7. Exception handlers ─────────────────────────────────────────────────
    for exc_type, handler in get_exception_handlers().items():
        app.add_exception_handler(exc_type, handler)

    for exc_type, handler in app_registry.get_all_exception_handlers().items():
        app.add_exception_handler(exc_type, handler)

    # ── 8. Routers ────────────────────────────────────────────────────────────
    for version, routers in app_registry.get_all_routers_by_version().items():
        prefix = "" if version == "internal" else f"/api/{version}"
        for router in routers:
            app.include_router(router, prefix=prefix)

    # ── 9. DI ─────────────────────────────────────────────────────────────────
    setup_di(app, container)

    return app
