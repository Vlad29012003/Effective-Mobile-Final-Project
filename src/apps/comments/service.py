from apps.comments.models import Comment
from apps.comments.repository import CommentRepository
from apps.comments.schemas import CreateCommentRequest, UpdateCommentRequest
from apps.tasks.models import Task
from apps.tasks.repository import TaskRepository
from apps.teams.models import TeamMemberRole
from apps.teams.repository import TeamMemberRepository
from packages.db.transaction import TransactionManager
from packages.errors import BaseError


class TaskNotFoundError(BaseError):
    code = "not_found"
    message = "Task not found"
    status_code = 404


class CommentNotFoundError(BaseError):
    code = "not_found"
    message = "Comment not found"
    status_code = 404


class NotTeamMemberError(BaseError):
    code = "insufficient_permissions"
    message = "You are not a member of this team"
    status_code = 403


class InsufficientRoleError(BaseError):
    code = "insufficient_permissions"
    message = "You don't have permission to perform this action"
    status_code = 403


class CommentService:
    def __init__(
        self,
        comment_repo: CommentRepository,
        task_repo: TaskRepository,
        member_repo: TeamMemberRepository,
        tx: TransactionManager,
    ) -> None:
        self._comment_repo = comment_repo
        self._task_repo = task_repo
        self._member_repo = member_repo
        self._tx = tx

    async def _require_member(self, team_id: int, user_id: int) -> None:
        if not await self._member_repo.get_member(team_id, user_id):
            raise NotTeamMemberError()

    async def _get_task_for_team(self, task_id: int, team_id: int) -> Task:
        task = await self._task_repo.get_by_id(task_id)
        if not task or task.team_id != team_id:
            raise TaskNotFoundError()
        return task

    async def _get_comment_for_task(self, comment_id: int, task_id: int) -> Comment:
        comment = await self._comment_repo.get_by_id(comment_id)
        if not comment or comment.task_id != task_id:
            raise CommentNotFoundError()
        return comment

    async def add_comment(
        self, user_id: int, team_id: int, task_id: int, data: CreateCommentRequest
    ) -> Comment:
        await self._require_member(team_id, user_id)
        await self._get_task_for_team(task_id, team_id)
        comment = Comment(task_id=task_id, author_id=user_id, text=data.text)
        async with self._tx:
            await self._comment_repo.add(comment)
        return comment

    async def list_comments(self, user_id: int, team_id: int, task_id: int) -> list[Comment]:
        await self._require_member(team_id, user_id)
        await self._get_task_for_team(task_id, team_id)
        return await self._comment_repo.list_for_task(task_id)

    async def update_comment(
        self,
        user_id: int,
        team_id: int,
        task_id: int,
        comment_id: int,
        data: UpdateCommentRequest,
    ) -> Comment:
        await self._require_member(team_id, user_id)
        comment = await self._get_comment_for_task(comment_id, task_id)
        if comment.author_id != user_id:
            raise InsufficientRoleError()
        comment.text = data.text
        async with self._tx:
            await self._comment_repo._session.flush()
        return comment

    async def delete_comment(
        self, user_id: int, team_id: int, task_id: int, comment_id: int
    ) -> None:
        member = await self._member_repo.get_member(team_id, user_id)
        if not member:
            raise NotTeamMemberError()
        comment = await self._get_comment_for_task(comment_id, task_id)
        is_author = comment.author_id == user_id
        is_privileged = member.role in (TeamMemberRole.admin, TeamMemberRole.manager)
        if not is_author and not is_privileged:
            raise InsufficientRoleError()
        async with self._tx:
            await self._comment_repo.delete(comment)
