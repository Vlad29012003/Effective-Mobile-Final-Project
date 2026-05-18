from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from apps.teams.models import TeamMemberRole


class CreateTeamRequest(BaseModel):
    name: str = Field(max_length=255)
    description: str | None = None


class UpdateTeamRequest(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = None


class TeamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    join_code: str
    created_by: int
    created_at: datetime


class MemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    team_id: int
    user_id: int
    role: TeamMemberRole
    joined_at: datetime


class UpdateMemberRoleRequest(BaseModel):
    role: TeamMemberRole
