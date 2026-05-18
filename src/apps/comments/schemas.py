from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateCommentRequest(BaseModel):
    text: str = Field(min_length=1)


class UpdateCommentRequest(BaseModel):
    text: str = Field(min_length=1)


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    author_id: int
    text: str
    created_at: datetime
    updated_at: datetime
