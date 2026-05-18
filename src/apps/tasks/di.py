from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from apps.tasks.repository import TaskRepository
from apps.tasks.service import TaskService
from apps.teams.repository import TeamMemberRepository
from packages.db.transaction import TransactionManager


class TasksProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def task_repository(self, session: AsyncSession) -> TaskRepository:
        return TaskRepository(session)

    @provide(scope=Scope.REQUEST)
    def task_service(
        self,
        task_repo: TaskRepository,
        member_repo: TeamMemberRepository,
        tx: TransactionManager,
    ) -> TaskService:
        return TaskService(task_repo, member_repo, tx)


provider = TasksProvider()
