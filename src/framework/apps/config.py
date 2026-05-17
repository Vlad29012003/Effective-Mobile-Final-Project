from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from .registry import AppRegistry


class SupportsProvider(Protocol):
    """Structural protocol for Dishka Provider-like objects."""

    ...


class AppConfig:
    """Base configuration class for feature apps.

    Each app should place a subclass of AppConfig in its `apps.py` module.
    Override `install()` to register all app components (routers, providers, etc).

    Example:
        class UsersApp(AppConfig):
            name = "apps.users"
            label = "users"

            def install(self, registry):
                from .api.v1.router import router
                registry.add_router("v1", router)

                from .di import provider
                registry.add_provider(provider)
    """

    name: str = ""
    label: str = ""
    enabled: bool = True

    def is_enabled(self) -> bool:
        return self.enabled

    def install(self, registry: "AppRegistry") -> None:
        """Register all app components into the registry.

        Override this method in each AppConfig subclass.
        """
        pass

    # kept for backward compatibility
    def get_provider(self) -> SupportsProvider | None:
        return None

    def get_router(self) -> Any | None:
        return None

    def get_routers(self) -> dict[str, Any] | None:
        return None

    def get_exception_handlers(self) -> dict[type[BaseException], Callable[..., Any]] | None:
        return None
