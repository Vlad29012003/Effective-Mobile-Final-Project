from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from apps.auth.dependencies import CurrentUser
from apps.evaluations.schemas import CreateEvaluationRequest, EvaluationResponse
from apps.evaluations.service import EvaluationService

router = APIRouter(
    prefix="/teams/{team_id}/tasks/{task_id}/evaluation",
    tags=["Evaluations"],
)
router.route_class = DishkaRoute


@router.post("", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED)
async def create_evaluation(
    team_id: int,
    task_id: int,
    body: CreateEvaluationRequest,
    current_user: CurrentUser,
    service: FromDishka[EvaluationService],
) -> EvaluationResponse:
    evaluation = await service.create_evaluation(int(current_user["sub"]), team_id, task_id, body)
    return EvaluationResponse.model_validate(evaluation)


@router.get("", response_model=EvaluationResponse)
async def get_evaluation(
    team_id: int,
    task_id: int,
    current_user: CurrentUser,
    service: FromDishka[EvaluationService],
) -> EvaluationResponse:
    evaluation = await service.get_evaluation(int(current_user["sub"]), team_id, task_id)
    return EvaluationResponse.model_validate(evaluation)
