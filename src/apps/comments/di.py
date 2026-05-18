from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from apps.comments.repository import CommentRepository
from apps.comments.service import CommentService
from apps.tasks.repository import TaskRepository
from apps.teams.repository import TeamMemberRepository
from packages.db.transaction import TransactionManager


class CommentsProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def comment_repository(self, session: AsyncSession) -> CommentRepository:
        return CommentRepository(session)

    @provide(scope=Scope.REQUEST)
    def comment_service(
        self,
        comment_repo: CommentRepository,
        task_repo: TaskRepository,
        member_repo: TeamMemberRepository,
        tx: TransactionManager,
    ) -> CommentService:
        return CommentService(comment_repo, task_repo, member_repo, tx)


provider = CommentsProvider()
