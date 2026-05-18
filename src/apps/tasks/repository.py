from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
        stmt = select(Task).where(Task.team_id == team_id)
        if status is not None:
            stmt = stmt.where(Task.status == status)
        if assignee_id is not None:
            stmt = stmt.where(Task.assignee_id == assignee_id)
        stmt = stmt.order_by(Task.created_at.desc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
