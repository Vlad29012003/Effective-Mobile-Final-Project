from datetime import datetime

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query

from apps.auth.dependencies import CurrentUser
from apps.calendar.schemas import CalendarResponse
from apps.calendar.service import CalendarService

router = APIRouter(
    prefix="/teams/{team_id}/calendar",
    tags=["Calendar"],
)
router.route_class = DishkaRoute


@router.get("", response_model=CalendarResponse)
async def get_calendar(
    team_id: int,
    current_user: CurrentUser,
    service: FromDishka[CalendarService],
    date_from: datetime = Query(..., description="Start of the date range (ISO 8601)"),
    date_to: datetime = Query(..., description="End of the date range (ISO 8601)"),
) -> CalendarResponse:
    return await service.get_calendar(int(current_user["sub"]), team_id, date_from, date_to)
