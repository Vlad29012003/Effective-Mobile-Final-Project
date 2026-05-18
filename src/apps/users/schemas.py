from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from apps.users.models import UserRole


class UserMeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    first_name: str | None
    last_name: str | None
    role: UserRole
    is_active: bool
    created_at: datetime


class UpdateProfileRequest(BaseModel):
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)


class JoinTeamRequest(BaseModel):
    join_code: str
