from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CreateMeetingRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    start_at: datetime
    end_at: datetime

    @model_validator(mode="after")
    def validate_time_range(self) -> "CreateMeetingRequest":
        if self.end_at <= self.start_at:
            raise ValueError("end_at must be after start_at")
        return self


class UpdateMeetingRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None


class MeetingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    team_id: int
    creator_id: int
    start_at: datetime
    end_at: datetime
    is_cancelled: bool
    created_at: datetime
