from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.teams.models import Team, TeamMember, TeamMemberRole
from apps.users.models import User
from apps.users.repository import UserRepository
from apps.users.schemas import UpdateProfileRequest
from packages.db.transaction import TransactionManager
from packages.errors import BaseError


class UserNotFoundError(BaseError):
    code = "not_found"
    message = "User not found"
    status_code = 404


class TeamNotFoundError(BaseError):
    code = "not_found"
    message = "Team with this join code not found"
    status_code = 404


class AlreadyTeamMemberError(BaseError):
    code = "unique"
    message = "You are already a member of this team"
    status_code = 409


class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
        session: AsyncSession,
        tx: TransactionManager,
    ) -> None:
        self._user_repo = user_repo
        self._session = session
        self._tx = tx

    async def get_me(self, user_id: int) -> User:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user

    async def update_profile(self, user_id: int, data: UpdateProfileRequest) -> User:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        if data.first_name is not None:
            user.first_name = data.first_name
        if data.last_name is not None:
            user.last_name = data.last_name
        async with self._tx:
            await self._session.flush()
        await self._session.refresh(user)
        return user

    async def join_team(self, user_id: int, join_code: str) -> TeamMember:
        result = await self._session.execute(select(Team).where(Team.join_code == join_code))
        team = result.scalar_one_or_none()
        if not team:
            raise TeamNotFoundError()

        existing = await self._session.execute(
            select(TeamMember).where(
                TeamMember.team_id == team.id,
                TeamMember.user_id == user_id,
            )
        )
        if existing.scalar_one_or_none():
            raise AlreadyTeamMemberError()

        member = TeamMember(
            team_id=team.id,
            user_id=user_id,
            role=TeamMemberRole.member,
        )
        async with self._tx:
            self._session.add(member)
            await self._session.flush()
            await self._session.refresh(member)
        return member
