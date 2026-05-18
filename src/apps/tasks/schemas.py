from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from apps.tasks.models import TaskStatus


class CreateTaskRequest(BaseModel):
    title: str = Field(max_length=255)
    description: str | None = None
    deadline: datetime | None = None
    assignee_id: int | None = None


class UpdateTaskRequest(BaseModel):
    title: str | None = Field(None, max_length=255)
    description: str | None = None
    deadline: datetime | None = None
    assignee_id: int | None = None


class ChangeStatusRequest(BaseModel):
    status: TaskStatus


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: TaskStatus
    deadline: datetime | None
    creator_id: int
    assignee_id: int | None
    team_id: int
    created_at: datetime
    updated_at: datetime
