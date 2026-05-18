from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.meetings.models import Meeting
from packages.db.repository import BaseRepository


class MeetingRepository(BaseRepository[Meeting]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Meeting)

    async def get_by_id(self, meeting_id: int) -> Meeting | None:
        return await self._session.get(Meeting, meeting_id)

    async def list_for_team(self, team_id: int) -> list[Meeting]:
        result = await self._session.execute(
            select(Meeting).where(Meeting.team_id == team_id).order_by(Meeting.start_at)
        )
        return list(result.scalars().all())

    async def has_overlap(
        self,
        team_id: int,
        start_at: datetime,
        end_at: datetime,
        exclude_id: int | None = None,
    ) -> bool:
        stmt = select(Meeting).where(
            and_(
                Meeting.team_id == team_id,
                Meeting.is_cancelled.is_(False),
                Meeting.start_at < end_at,
                Meeting.end_at > start_at,
            )
        )
        if exclude_id is not None:
            stmt = stmt.where(Meeting.id != exclude_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
