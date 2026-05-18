from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from apps.auth.dependencies import CurrentUser
from apps.teams.schemas import (
    CreateTeamRequest,
    MemberResponse,
    TeamResponse,
    UpdateMemberRoleRequest,
    UpdateTeamRequest,
)
from apps.teams.service import TeamService

router = APIRouter(prefix="/teams", tags=["Teams"])
router.route_class = DishkaRoute


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    body: CreateTeamRequest,
    current_user: CurrentUser,
    service: FromDishka[TeamService],
) -> TeamResponse:
    team = await service.create_team(int(current_user["sub"]), body)
    return TeamResponse.model_validate(team)


@router.get("", response_model=list[TeamResponse])
async def list_my_teams(
    current_user: CurrentUser,
    service: FromDishka[TeamService],
) -> list[TeamResponse]:
    teams = await service.get_my_teams(int(current_user["sub"]))
    return [TeamResponse.model_validate(t) for t in teams]


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    current_user: CurrentUser,
    service: FromDishka[TeamService],
) -> TeamResponse:
    team = await service.get_team(team_id, int(current_user["sub"]))
    return TeamResponse.model_validate(team)


@router.patch("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    body: UpdateTeamRequest,
    current_user: CurrentUser,
    service: FromDishka[TeamService],
) -> TeamResponse:
    team = await service.update_team(team_id, int(current_user["sub"]), body)
    return TeamResponse.model_validate(team)


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: int,
    current_user: CurrentUser,
    service: FromDishka[TeamService],
) -> None:
    await service.delete_team(team_id, int(current_user["sub"]))


@router.get("/{team_id}/members", response_model=list[MemberResponse])
async def list_members(
    team_id: int,
    current_user: CurrentUser,
    service: FromDishka[TeamService],
) -> list[MemberResponse]:
    members = await service.get_members(team_id, int(current_user["sub"]))
    return [MemberResponse.model_validate(m) for m in members]


@router.patch(
    "/{team_id}/members/{user_id}",
    response_model=MemberResponse,
)
async def update_member_role(
    team_id: int,
    user_id: int,
    body: UpdateMemberRoleRequest,
    current_user: CurrentUser,
    service: FromDishka[TeamService],
) -> MemberResponse:
    member = await service.update_member_role(team_id, int(current_user["sub"]), user_id, body.role)
    return MemberResponse.model_validate(member)


@router.delete(
    "/{team_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_member(
    team_id: int,
    user_id: int,
    current_user: CurrentUser,
    service: FromDishka[TeamService],
) -> None:
    await service.remove_member(team_id, int(current_user["sub"]), user_id)
