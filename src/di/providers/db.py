from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from configs import Settings
from packages.db import TransactionManager, make_engine, make_session_factory


class DBProvider(Provider):
    @provide(scope=Scope.APP)
    async def engine(self, settings: Settings) -> AsyncIterable[AsyncEngine]:
        engine = make_engine(
            url=settings.get_database_url(),
            echo=settings.DEBUG,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
        )
        try:
            yield engine
        finally:
            await engine.dispose()

    @provide(scope=Scope.APP)
    def session_factory(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return make_session_factory(engine)

    @provide(scope=Scope.REQUEST)
    async def session(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with session_factory() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def transaction_manager(self, session: AsyncSession) -> TransactionManager:
        return TransactionManager(session)

    @provide(scope=Scope.APP)
    def sync_engine(self, settings: Settings) -> Engine:
        sync_url = settings.get_sync_database_url()
        if not sync_url:
            raise ValueError(
                "No sync database URL configured. "
                "Set SYNC_DATABASE_URL or SYNC_DB_DRIVER in your environment."
            )
        kwargs: dict[str, object] = {"pool_pre_ping": True, "echo": settings.DEBUG}
        if settings.DB_POOL_SIZE is not None:
            kwargs["pool_size"] = settings.DB_POOL_SIZE
        if settings.DB_MAX_OVERFLOW is not None:
            kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW
        return create_engine(sync_url, **kwargs)
