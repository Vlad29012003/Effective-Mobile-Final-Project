from apps.evaluations.models import Evaluation
from apps.evaluations.repository import EvaluationRepository
from apps.evaluations.schemas import CreateEvaluationRequest
from apps.tasks.models import Task, TaskStatus
from apps.tasks.repository import TaskRepository
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
    message = "Only admin or manager can evaluate tasks"
    status_code = 403


class TaskNotDoneError(BaseError):
    code = "invalid_state"
    message = "Task must be in 'done' status to be evaluated"
    status_code = 422


class EvaluationAlreadyExistsError(BaseError):
    code = "already_exists"
    message = "This task has already been evaluated"
    status_code = 409


class EvaluationNotFoundError(BaseError):
    code = "not_found"
    message = "Evaluation not found"
    status_code = 404


class EvaluationService:
    def __init__(
        self,
        evaluation_repo: EvaluationRepository,
        task_repo: TaskRepository,
        member_repo: TeamMemberRepository,
        tx: TransactionManager,
    ) -> None:
        self._evaluation_repo = evaluation_repo
        self._task_repo = task_repo
        self._member_repo = member_repo
        self._tx = tx

    async def _require_privileged(self, team_id: int, user_id: int) -> None:
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

    async def create_evaluation(
        self,
        user_id: int,
        team_id: int,
        task_id: int,
        data: CreateEvaluationRequest,
    ) -> Evaluation:
        await self._require_privileged(team_id, user_id)
        task = await self._get_task_for_team(task_id, team_id)
        if task.status != TaskStatus.done:
            raise TaskNotDoneError()
        existing = await self._evaluation_repo.get_by_task_id(task_id)
        if existing:
            raise EvaluationAlreadyExistsError()
        evaluation = Evaluation(
            task_id=task_id,
            evaluator_id=user_id,
            score=data.score,
            comment=data.comment,
        )
        async with self._tx:
            await self._evaluation_repo.add(evaluation)
        return evaluation

    async def get_evaluation(
        self,
        user_id: int,
        team_id: int,
        task_id: int,
    ) -> Evaluation:
        member = await self._member_repo.get_member(team_id, user_id)
        if not member:
            raise NotTeamMemberError()
        await self._get_task_for_team(task_id, team_id)
        evaluation = await self._evaluation_repo.get_by_task_id(task_id)
        if not evaluation:
            raise EvaluationNotFoundError()
        return evaluation
