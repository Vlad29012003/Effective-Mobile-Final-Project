from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateEvaluationRequest(BaseModel):
    score: int = Field(ge=1, le=5)
    comment: str | None = None


class EvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    evaluator_id: int
    score: int
    comment: str | None
    created_at: datetime
