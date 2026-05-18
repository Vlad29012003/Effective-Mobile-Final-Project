from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query, status

from apps.auth.dependencies import CurrentUser
from apps.tasks.models import TaskStatus
from apps.tasks.schemas import (
    ChangeStatusRequest,
    CreateTaskRequest,
    TaskResponse,
    UpdateTaskRequest,
)
from apps.tasks.service import TaskService

router = APIRouter(prefix="/teams/{team_id}/tasks", tags=["Tasks"])
router.route_class = DishkaRoute


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    team_id: int,
    body: CreateTaskRequest,
    current_user: CurrentUser,
    service: FromDishka[TaskService],
) -> TaskResponse:
    task = await service.create_task(int(current_user["sub"]), team_id, body)
    return TaskResponse.model_validate(task)


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    team_id: int,
    current_user: CurrentUser,
    service: FromDishka[TaskService],
    task_status: TaskStatus | None = Query(None, alias="status"),
    assignee_id: int | None = Query(None),
) -> list[TaskResponse]:
    tasks = await service.list_tasks(
        int(current_user["sub"]),
        team_id,
        status=task_status,
        assignee_id=assignee_id,
    )
    return [TaskResponse.model_validate(t) for t in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    team_id: int,
    task_id: int,
    current_user: CurrentUser,
    service: FromDishka[TaskService],
) -> TaskResponse:
    task = await service.get_task(int(current_user["sub"]), team_id, task_id)
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    team_id: int,
    task_id: int,
    body: UpdateTaskRequest,
    current_user: CurrentUser,
    service: FromDishka[TaskService],
) -> TaskResponse:
    task = await service.update_task(int(current_user["sub"]), team_id, task_id, body)
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    team_id: int,
    task_id: int,
    current_user: CurrentUser,
    service: FromDishka[TaskService],
) -> None:
    await service.delete_task(int(current_user["sub"]), team_id, task_id)


@router.patch("/{task_id}/status", response_model=TaskResponse)
async def change_status(
    team_id: int,
    task_id: int,
    body: ChangeStatusRequest,
    current_user: CurrentUser,
    service: FromDishka[TaskService],
) -> TaskResponse:
    task = await service.change_status(int(current_user["sub"]), team_id, task_id, body.status)
    return TaskResponse.model_validate(task)
