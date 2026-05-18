from typing import TYPE_CHECKING

from framework.apps.config import AppConfig

if TYPE_CHECKING:
    from framework.apps.registry import AppRegistry


class CalendarApp(AppConfig):
    name = "apps.calendar"
    label = "calendar"

    def install(self, registry: "AppRegistry") -> None:
        from .api.v1.router import router

        registry.add_router("v1", router, app_name=self.name)

        from .di import provider

        registry.add_provider(provider)
