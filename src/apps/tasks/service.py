from apps.tasks.models import Task, TaskStatus
from apps.tasks.repository import TaskRepository
from apps.tasks.schemas import CreateTaskRequest, UpdateTaskRequest
from apps.teams.models import TeamMemberRole
from apps.teams.repository import TeamMemberRepository
from packages.db.transaction import TransactionManager
from packages.errors import BaseError


class TaskNotFoundError(BaseError):
    code = "not_found"
    message = "Task not found"
    status_code = 404


class NotTeamMemberError(BaseError):
    code = "insufficient_permissions"
    message = "You are not a member of this team"
    status_code = 403


class InsufficientRoleError(BaseError):
    code = "insufficient_permissions"
    message = "You don't have permission to perform this action"
    status_code = 403


class TaskService:
    def __init__(
        self,
        task_repo: TaskRepository,
        member_repo: TeamMemberRepository,
        tx: TransactionManager,
    ) -> None:
        self._task_repo = task_repo
        self._member_repo = member_repo
        self._tx = tx

    async def _require_member(self, team_id: int, user_id: int) -> None:
        member = await self._member_repo.get_member(team_id, user_id)
        if not member:
            raise NotTeamMemberError()

    async def _require_manager_or_admin(self, team_id: int, user_id: int) -> None:
        member = await self._member_repo.get_member(team_id, user_id)
        if not member:
            raise NotTeamMemberError()
        if member.role not in (TeamMemberRole.admin, TeamMemberRole.manager):
            raise InsufficientRoleError()

    async def _get_task_for_team(self, task_id: int, team_id: int) -> Task:
        task = await self._task_repo.get_by_id(task_id)
        if not task or task.team_id != team_id:
            raise TaskNotFoundError()
        return task

    async def create_task(self, user_id: int, team_id: int, data: CreateTaskRequest) -> Task:
        await self._require_manager_or_admin(team_id, user_id)
        task = Task(
            title=data.title,
            description=data.description,
            deadline=data.deadline,
            assignee_id=data.assignee_id,
            team_id=team_id,
            creator_id=user_id,
        )
        async with self._tx:
            await self._task_repo.add(task)
        return task

    async def list_tasks(
        self,
        user_id: int,
        team_id: int,
        *,
        status: TaskStatus | None = None,
        assignee_id: int | None = None,
    ) -> list[Task]:
        await self._require_member(team_id, user_id)
        return await self._task_repo.list_for_team(team_id, status=status, assignee_id=assignee_id)

    async def get_task(self, user_id: int, team_id: int, task_id: int) -> Task:
        await self._require_member(team_id, user_id)
        return await self._get_task_for_team(task_id, team_id)

    async def update_task(
        self, user_id: int, team_id: int, task_id: int, data: UpdateTaskRequest
    ) -> Task:
        await self._require_manager_or_admin(team_id, user_id)
        task = await self._get_task_for_team(task_id, team_id)
        if data.title is not None:
            task.title = data.title
        if data.description is not None:
            task.description = data.description
        if data.deadline is not None:
            task.deadline = data.deadline
        if data.assignee_id is not None:
            task.assignee_id = data.assignee_id
        async with self._tx:
            await self._task_repo._session.flush()
        return task

    async def delete_task(self, user_id: int, team_id: int, task_id: int) -> None:
        await self._require_manager_or_admin(team_id, user_id)
        task = await self._get_task_for_team(task_id, team_id)
        async with self._tx:
            await self._task_repo.delete(task)

    async def change_status(
        self, user_id: int, team_id: int, task_id: int, status: TaskStatus
    ) -> Task:
        member = await self._member_repo.get_member(team_id, user_id)
        if not member:
            raise NotTeamMemberError()

        task = await self._get_task_for_team(task_id, team_id)

        is_assignee = task.assignee_id == user_id
        is_privileged = member.role in (TeamMemberRole.admin, TeamMemberRole.manager)
        if not is_assignee and not is_privileged:
            raise InsufficientRoleError()

        task.status = status
        async with self._tx:
            await self._task_repo._session.flush()
        return task
