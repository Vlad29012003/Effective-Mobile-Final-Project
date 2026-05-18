from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from apps.users.models import UserRole


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserMeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    first_name: str | None
    last_name: str | None
    role: UserRole
    is_active: bool
    created_at: datetime
