from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from apps.meetings.repository import MeetingRepository
from apps.meetings.service import MeetingService
from apps.teams.repository import TeamMemberRepository
from packages.db.transaction import TransactionManager


class MeetingsProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def meeting_repository(self, session: AsyncSession) -> MeetingRepository:
        return MeetingRepository(session)

    @provide(scope=Scope.REQUEST)
    def meeting_service(
        self,
        meeting_repo: MeetingRepository,
        member_repo: TeamMemberRepository,
        tx: TransactionManager,
    ) -> MeetingService:
        return MeetingService(meeting_repo, member_repo, tx)


provider = MeetingsProvider()
