from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession


class TransactionManager:
    """Lightweight transaction helper wrapping AsyncSession.

    Usage:
        async with tx:
            repo.add(...)
            await tx.flush()
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def __aenter__(self) -> "TransactionManager":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if exc_type:
            await self._session.rollback()
        else:
            await self._session.commit()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def flush(self) -> None:
        await self._session.flush()

    def add(self, instance: object) -> None:
        self._session.add(instance)
