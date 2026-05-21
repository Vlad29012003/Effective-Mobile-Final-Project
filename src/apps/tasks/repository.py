from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from apps.tasks.models import Task, TaskStatus
from packages.db.repository import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Task)

    async def get_by_id(self, task_id: int) -> Task | None:
        return await self._session.get(Task, task_id)

    async def list_for_team(
        self,
        team_id: int,
        *,
        status: TaskStatus | None = None,
        assignee_id: int | None = None,
    ) -> list[Task]:
        stmt = select(Task).options(joinedload(Task.assignee)).where(Task.team_id == team_id)
        if status is not None:
            stmt = stmt.where(Task.status == status)
        if assignee_id is not None:
            stmt = stmt.where(Task.assignee_id == assignee_id)
        stmt = stmt.order_by(Task.created_at.desc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_for_team_by_deadline_range(
        self,
        team_id: int,
        date_from: datetime,
        date_to: datetime,
    ) -> list[Task]:
        stmt = (
            select(Task)
            .where(
                and_(
                    Task.team_id == team_id,
                    Task.deadline.isnot(None),
                    Task.deadline >= date_from,
                    Task.deadline <= date_to,
                )
            )
            .order_by(Task.deadline)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
