from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from apps.teams.models import Team, TeamMember
from packages.db.repository import BaseRepository


class TeamRepository(BaseRepository[Team]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Team)

    async def get_by_id(self, team_id: int) -> Team | None:
        return await self._session.get(Team, team_id)

    async def get_user_teams(self, user_id: int) -> list[Team]:
        result = await self._session.execute(
            select(Team)
            .join(TeamMember, TeamMember.team_id == Team.id)
            .where(TeamMember.user_id == user_id)
            .order_by(Team.created_at.desc())
        )
        return list(result.scalars().all())


class TeamMemberRepository(BaseRepository[TeamMember]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, TeamMember)

    async def get_member(self, team_id: int, user_id: int) -> TeamMember | None:
        result = await self._session.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_team_members(self, team_id: int) -> list[TeamMember]:
        result = await self._session.execute(
            select(TeamMember)
            .options(joinedload(TeamMember.user))
            .where(TeamMember.team_id == team_id)
            .order_by(TeamMember.joined_at)
        )
        return list(result.scalars().all())
