from datetime import datetime

from pydantic import BaseModel, ConfigDict

from apps.tasks.models import TaskStatus


class CalendarTaskItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: TaskStatus
    deadline: datetime
    assignee_id: int | None
    team_id: int


class CalendarMeetingItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    start_at: datetime
    end_at: datetime
    team_id: int


class CalendarResponse(BaseModel):
    tasks: list[CalendarTaskItem]
    meetings: list[CalendarMeetingItem]
