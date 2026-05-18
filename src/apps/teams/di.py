from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from apps.teams.repository import TeamMemberRepository, TeamRepository
from apps.teams.service import TeamService
from packages.db.transaction import TransactionManager


class TeamsProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def team_repository(self, session: AsyncSession) -> TeamRepository:
        return TeamRepository(session)

    @provide(scope=Scope.REQUEST)
    def team_member_repository(self, session: AsyncSession) -> TeamMemberRepository:
        return TeamMemberRepository(session)

    @provide(scope=Scope.REQUEST)
    def team_service(
        self,
        team_repo: TeamRepository,
        member_repo: TeamMemberRepository,
        tx: TransactionManager,
    ) -> TeamService:
        return TeamService(team_repo, member_repo, tx)


provider = TeamsProvider()
