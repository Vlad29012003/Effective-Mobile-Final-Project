from datetime import UTC, datetime, timedelta
from pathlib import Path

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from apps.calendar.service import CalendarService
from apps.teams.service import TeamService
from packages.errors import BaseError
from presentations.web.deps import get_web_user

router = APIRouter(tags=["Web:Calendar"])
router.route_class = DishkaRoute

_templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


@router.get("/teams/{team_id}/calendar")
async def calendar_page(
    request: Request,
    team_id: int,
    team_service: FromDishka[TeamService],
    calendar_service: FromDishka[CalendarService],
    date_from: str = Query(default=""),
    date_to: str = Query(default=""),
):
    user = get_web_user(request)
    if user is None:
        return RedirectResponse("/web/auth/login", status_code=303)

    user_id = int(user["sub"])

    now = datetime.now(UTC)
    if not date_from:
        date_from = now.replace(day=1).strftime("%Y-%m-%d")
    if not date_to:
        next_month = (now.replace(day=28) + timedelta(days=4)).replace(day=1)
        date_to = (next_month - timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        team = await team_service.get_team(team_id, user_id)
        from_dt = datetime.fromisoformat(f"{date_from}T00:00:00+00:00")
        to_dt = datetime.fromisoformat(f"{date_to}T23:59:59+00:00")
        calendar = await calendar_service.get_calendar(user_id, team_id, from_dt, to_dt)
    except BaseError:
        return RedirectResponse("/web/dashboard?error=Команда+не+найдена", status_code=303)

    return _templates.TemplateResponse(
        request,
        "calendar/index.html",
        {
            "user": user,
            "team": team,
            "calendar": calendar,
            "date_from": date_from,
            "date_to": date_to,
        },
    )
