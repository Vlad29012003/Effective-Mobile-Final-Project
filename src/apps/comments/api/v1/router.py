from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from apps.auth.dependencies import CurrentUser
from apps.comments.schemas import CommentResponse, CreateCommentRequest, UpdateCommentRequest
from apps.comments.service import CommentService

router = APIRouter(
    prefix="/teams/{team_id}/tasks/{task_id}/comments",
    tags=["Comments"],
)
router.route_class = DishkaRoute


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def add_comment(
    team_id: int,
    task_id: int,
    body: CreateCommentRequest,
    current_user: CurrentUser,
    service: FromDishka[CommentService],
) -> CommentResponse:
    comment = await service.add_comment(int(current_user["sub"]), team_id, task_id, body)
    return CommentResponse.model_validate(comment)


@router.get("", response_model=list[CommentResponse])
async def list_comments(
    team_id: int,
    task_id: int,
    current_user: CurrentUser,
    service: FromDishka[CommentService],
) -> list[CommentResponse]:
    comments = await service.list_comments(int(current_user["sub"]), team_id, task_id)
    return [CommentResponse.model_validate(c) for c in comments]


@router.patch("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    team_id: int,
    task_id: int,
    comment_id: int,
    body: UpdateCommentRequest,
    current_user: CurrentUser,
    service: FromDishka[CommentService],
) -> CommentResponse:
    comment = await service.update_comment(
        int(current_user["sub"]), team_id, task_id, comment_id, body
    )
    return CommentResponse.model_validate(comment)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    team_id: int,
    task_id: int,
    comment_id: int,
    current_user: CurrentUser,
    service: FromDishka[CommentService],
) -> None:
    await service.delete_comment(int(current_user["sub"]), team_id, task_id, comment_id)
