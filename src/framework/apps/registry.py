from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fastapi import APIRouter


class AppRegistry:
    """Central registry for application-level components.

    Each app calls `registry.add_*` methods inside its AppConfig.install()
    to register HTTP routers, DI providers, and exception handlers.
    """

    def __init__(self) -> None:
        self._routers: dict[str, dict[str, APIRouter]] = {}
        self._exception_handlers: dict[str, dict] = {}
        self._providers: list[Any] = []

    # ── HTTP ──────────────────────────────────────────────────────────────────

    def add_router(
        self,
        version: str,
        router: APIRouter,
        *,
        app_name: str | None = None,
    ) -> None:
        app_name = app_name or "default"
        self._routers.setdefault(app_name, {})[version] = router

    def add_exception_handler(
        self,
        exc_type: type[Exception],
        handler: Callable,
        *,
        app_name: str | None = None,
    ) -> None:
        app_name = app_name or "default"
        self._exception_handlers.setdefault(app_name, {})[exc_type] = handler

    def get_all_routers_by_version(self) -> dict[str, list[APIRouter]]:
        result: dict[str, list[APIRouter]] = {}
        for app_routers in self._routers.values():
            for version, router in app_routers.items():
                result.setdefault(version, []).append(router)
        return result

    def get_all_exception_handlers(self) -> dict[type[Exception], Callable]:
        result: dict[type[Exception], Callable] = {}
        for app_handlers in self._exception_handlers.values():
            result.update(app_handlers)
        return result

    # ── DI ───────────────────────────────────────────────────────────────────

    def add_provider(self, provider: Any) -> None:
        if provider is not None:
            self._providers.append(provider)

    def get_all_providers(self) -> list[Any]:
        return self._providers.copy()
