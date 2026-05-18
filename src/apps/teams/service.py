import secrets

from apps.teams.models import Team, TeamMember, TeamMemberRole
from apps.teams.repository import TeamMemberRepository, TeamRepository
from apps.teams.schemas import CreateTeamRequest, UpdateTeamRequest
from packages.db.transaction import TransactionManager
from packages.errors import BaseError


class TeamNotFoundError(BaseError):
    code = "not_found"
    message = "Team not found"
    status_code = 404


class NotTeamMemberError(BaseError):
    code = "insufficient_permissions"
    message = "You are not a member of this team"
    status_code = 403


class InsufficientRoleError(BaseError):
    code = "insufficient_permissions"
    message = "You don't have permission to perform this action"
    status_code = 403


class MemberNotFoundError(BaseError):
    code = "not_found"
    message = "Member not found in this team"
    status_code = 404


class CannotRemoveSelfError(BaseError):
    code = "invalid"
    message = "You cannot remove yourself from the team"
    status_code = 400


def _require_role(member: TeamMember, *allowed: TeamMemberRole) -> None:
    if member.role not in allowed:
        raise InsufficientRoleError()


class TeamService:
    def __init__(
        self,
        team_repo: TeamRepository,
        member_repo: TeamMemberRepository,
        tx: TransactionManager,
    ) -> None:
        self._team_repo = team_repo
        self._member_repo = member_repo
        self._tx = tx

    async def _get_team_or_404(self, team_id: int) -> Team:
        team = await self._team_repo.get_by_id(team_id)
        if not team:
            raise TeamNotFoundError()
        return team

    async def _get_member_or_403(self, team_id: int, user_id: int) -> TeamMember:
        member = await self._member_repo.get_member(team_id, user_id)
        if not member:
            raise NotTeamMemberError()
        return member

    async def create_team(self, user_id: int, data: CreateTeamRequest) -> Team:
        join_code = secrets.token_hex(16)
        team = Team(
            name=data.name,
            description=data.description,
            join_code=join_code,
            created_by=user_id,
        )
        async with self._tx:
            await self._team_repo.add(team)
            await self._member_repo.add(
                TeamMember(
                    team_id=team.id,
                    user_id=user_id,
                    role=TeamMemberRole.admin,
                )
            )
        return team

    async def get_my_teams(self, user_id: int) -> list[Team]:
        return await self._team_repo.get_user_teams(user_id)

    async def get_team(self, team_id: int, user_id: int) -> Team:
        team = await self._get_team_or_404(team_id)
        await self._get_member_or_403(team_id, user_id)
        return team

    async def update_team(self, team_id: int, user_id: int, data: UpdateTeamRequest) -> Team:
        team = await self._get_team_or_404(team_id)
        member = await self._get_member_or_403(team_id, user_id)
        _require_role(member, TeamMemberRole.admin)

        if data.name is not None:
            team.name = data.name
        if data.description is not None:
            team.description = data.description
        async with self._tx:
            pass
        return team

    async def delete_team(self, team_id: int, user_id: int) -> None:
        team = await self._get_team_or_404(team_id)
        member = await self._get_member_or_403(team_id, user_id)
        _require_role(member, TeamMemberRole.admin)
        async with self._tx:
            await self._team_repo.delete(team)

    async def get_members(self, team_id: int, user_id: int) -> list[TeamMember]:
        await self._get_team_or_404(team_id)
        await self._get_member_or_403(team_id, user_id)
        return await self._member_repo.get_team_members(team_id)

    async def update_member_role(
        self,
        team_id: int,
        actor_id: int,
        target_user_id: int,
        role: TeamMemberRole,
    ) -> TeamMember:
        await self._get_team_or_404(team_id)
        actor = await self._get_member_or_403(team_id, actor_id)
        _require_role(actor, TeamMemberRole.admin)

        target = await self._member_repo.get_member(team_id, target_user_id)
        if not target:
            raise MemberNotFoundError()

        target.role = role
        async with self._tx:
            pass
        return target

    async def remove_member(self, team_id: int, actor_id: int, target_user_id: int) -> None:
        await self._get_team_or_404(team_id)
        actor = await self._get_member_or_403(team_id, actor_id)
        _require_role(actor, TeamMemberRole.admin, TeamMemberRole.manager)

        if actor_id == target_user_id:
            raise CannotRemoveSelfError()

        target = await self._member_repo.get_member(team_id, target_user_id)
        if not target:
            raise MemberNotFoundError()

        # manager не может удалять admin-а
        if actor.role == TeamMemberRole.manager and target.role == TeamMemberRole.admin:
            raise InsufficientRoleError()

        async with self._tx:
            await self._member_repo.delete(target)
