from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from apps.auth.dependencies import CurrentUser
from apps.meetings.schemas import CreateMeetingRequest, MeetingResponse, UpdateMeetingRequest
from apps.meetings.service import MeetingService

router = APIRouter(
    prefix="/teams/{team_id}/meetings",
    tags=["Meetings"],
)
router.route_class = DishkaRoute


@router.post("", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
async def create_meeting(
    team_id: int,
    body: CreateMeetingRequest,
    current_user: CurrentUser,
    service: FromDishka[MeetingService],
) -> MeetingResponse:
    meeting = await service.create_meeting(int(current_user["sub"]), team_id, body)
    return MeetingResponse.model_validate(meeting)


@router.get("", response_model=list[MeetingResponse])
async def list_meetings(
    team_id: int,
    current_user: CurrentUser,
    service: FromDishka[MeetingService],
) -> list[MeetingResponse]:
    meetings = await service.list_meetings(int(current_user["sub"]), team_id)
    return [MeetingResponse.model_validate(m) for m in meetings]


@router.patch("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    team_id: int,
    meeting_id: int,
    body: UpdateMeetingRequest,
    current_user: CurrentUser,
    service: FromDishka[MeetingService],
) -> MeetingResponse:
    meeting = await service.update_meeting(int(current_user["sub"]), team_id, meeting_id, body)
    return MeetingResponse.model_validate(meeting)


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_meeting(
    team_id: int,
    meeting_id: int,
    current_user: CurrentUser,
    service: FromDishka[MeetingService],
) -> None:
    await service.cancel_meeting(int(current_user["sub"]), team_id, meeting_id)
