from dishka import Provider, Scope, provide

from configs import Settings, settings


class ConfigProvider(Provider):
    @provide(scope=Scope.APP)
    def get_settings(self) -> Settings:
        return settings
