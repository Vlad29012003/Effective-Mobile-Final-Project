from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from apps.auth.dependencies import CurrentUser
from apps.users.schemas import JoinTeamRequest, UpdateProfileRequest, UserMeResponse
from apps.users.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])
router.route_class = DishkaRoute


@router.get("/me", response_model=UserMeResponse)
async def get_me(
    current_user: CurrentUser,
    service: FromDishka[UserService],
) -> UserMeResponse:
    user = await service.get_me(int(current_user["sub"]))
    return UserMeResponse.model_validate(user)


@router.patch("/me", response_model=UserMeResponse)
async def update_profile(
    body: UpdateProfileRequest,
    current_user: CurrentUser,
    service: FromDishka[UserService],
) -> UserMeResponse:
    user = await service.update_profile(int(current_user["sub"]), body)
    return UserMeResponse.model_validate(user)


@router.post("/join", status_code=status.HTTP_200_OK)
async def join_team(
    body: JoinTeamRequest,
    current_user: CurrentUser,
    service: FromDishka[UserService],
) -> dict[str, str]:
    await service.join_team(int(current_user["sub"]), body.join_code)
    return {"detail": "Successfully joined the team"}
