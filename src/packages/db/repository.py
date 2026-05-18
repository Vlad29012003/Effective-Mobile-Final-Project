from collections.abc import Sequence
from typing import Any, Generic, TypeVar, cast

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.elements import ColumnElement

ModelT = TypeVar("ModelT", bound=DeclarativeBase)


class BaseRepository(Generic[ModelT]):
    """Generic repository for SQLAlchemy models.

    - No commit/rollback — managed externally by TransactionManager
    - Provides common CRUD + pagination helpers
    """

    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        self._session = session
        self._model = model

    async def add(self, instance: ModelT) -> ModelT:
        self._session.add(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def get_by_id(self, id_: int) -> ModelT | None:
        result = await self._session.get(self._model, id_)
        return cast(ModelT | None, result)

    async def list_all(self) -> list[ModelT]:
        result = await self._session.execute(select(self._model))
        return cast(list[ModelT], result.scalars().all())

    async def delete(self, instance: ModelT) -> None:
        await self._session.delete(instance)

    async def filter_by(self, **kwargs: Any) -> list[ModelT]:
        result = await self._session.execute(select(self._model).filter_by(**kwargs))
        return cast(list[ModelT], result.scalars().all())

    async def exists(self, **kwargs: Any) -> bool:
        stmt = select(func.count()).select_from(self._model).filter_by(**kwargs)
        result = await self._session.execute(stmt)
        return int(result.scalar_one() or 0) > 0

    async def paginate(
        self,
        *,
        page: int,
        page_size: int,
        where: ColumnElement[bool] | None = None,
        order_by: Sequence[ColumnElement[Any]] | None = None,
        sort: str | None = None,
    ) -> tuple[list[ModelT], int]:
        if page < 1:
            page = 1
        offset = (page - 1) * page_size

        base = select(self._model)
        if where is not None:
            base = base.where(where)

        # Parse "field:asc,other:desc" or "-field" sort strings
        if sort:
            cols: list[ColumnElement[Any]] = []
            for part in sort.split(","):
                part = part.strip()
                if not part:
                    continue
                direction = "asc"
                name = part
                if ":" in part:
                    name, direction = part.split(":", 1)
                elif part.startswith("-"):
                    name = part[1:]
                    direction = "desc"
                col = getattr(self._model, name, None)
                if col is None:
                    continue
                typed_col = cast(ColumnElement[Any], col)
                cols.append(typed_col.asc() if direction.lower() == "asc" else typed_col.desc())
            if cols:
                base = base.order_by(*cols)
        elif order_by:
            base = base.order_by(*order_by)

        data_result = await self._session.execute(base.offset(offset).limit(page_size))
        items = cast(list[ModelT], data_result.scalars().all())

        count_stmt = select(func.count()).select_from(self._model)
        if where is not None:
            count_stmt = count_stmt.where(where)
        count_result = await self._session.execute(count_stmt)
        total = int(count_result.scalar_one() or 0)

        return items, total
