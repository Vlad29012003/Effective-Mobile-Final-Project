from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide

from configs import Settings
from packages.redis.client import RedisClient


class RedisProvider(Provider):
    @provide(scope=Scope.APP)
    async def redis_client(self, settings: Settings) -> AsyncIterable[RedisClient]:
        if not settings.REDIS_URL:
            raise RuntimeError("REDIS_URL is required but not configured")
        client = RedisClient(settings.REDIS_URL)
        try:
            yield client
        finally:
            await client.close()
