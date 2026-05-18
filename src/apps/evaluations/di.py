from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from apps.evaluations.repository import EvaluationRepository
from apps.evaluations.service import EvaluationService
from apps.tasks.repository import TaskRepository
from apps.teams.repository import TeamMemberRepository
from packages.db.transaction import TransactionManager


class EvaluationsProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def evaluation_repository(self, session: AsyncSession) -> EvaluationRepository:
        return EvaluationRepository(session)

    @provide(scope=Scope.REQUEST)
    def evaluation_service(
        self,
        evaluation_repo: EvaluationRepository,
        task_repo: TaskRepository,
        member_repo: TeamMemberRepository,
        tx: TransactionManager,
    ) -> EvaluationService:
        return EvaluationService(evaluation_repo, task_repo, member_repo, tx)


provider = EvaluationsProvider()
