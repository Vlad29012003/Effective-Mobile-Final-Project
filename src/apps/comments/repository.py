from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from apps.comments.models import Comment
from packages.db.repository import BaseRepository


class CommentRepository(BaseRepository[Comment]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Comment)

    async def get_by_id(self, comment_id: int) -> Comment | None:
        return await self._session.get(Comment, comment_id)

    async def list_for_task(self, task_id: int) -> list[Comment]:
        result = await self._session.execute(
            select(Comment)
            .options(joinedload(Comment.author))
            .where(Comment.task_id == task_id)
            .order_by(Comment.created_at)
        )
        return list(result.scalars().all())
