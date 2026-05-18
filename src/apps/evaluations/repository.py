from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.evaluations.models import Evaluation
from packages.db.repository import BaseRepository


class EvaluationRepository(BaseRepository[Evaluation]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Evaluation)

    async def get_by_task_id(self, task_id: int) -> Evaluation | None:
        result = await self._session.execute(
            select(Evaluation).where(Evaluation.task_id == task_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, evaluation_id: int) -> Evaluation | None:
        return await self._session.get(Evaluation, evaluation_id)
