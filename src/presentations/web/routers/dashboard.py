from pathlib import Path

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from apps.teams.schemas import CreateTeamRequest
from apps.teams.service import TeamService
from apps.users.service import UserService
from packages.errors import BaseError
from presentations.web.deps import get_web_user

router = APIRouter(tags=["Web:Dashboard"])
router.route_class = DishkaRoute

_templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


@router.get("/dashboard")
async def dashboard(request: Request, service: FromDishka[TeamService]):
    user = get_web_user(request)
    if user is None:
        return RedirectResponse("/web/auth/login", status_code=303)

    teams = await service.get_my_teams(int(user["sub"]))
    return _templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "user": user,
            "teams": teams,
            "error": request.query_params.get("error"),
            "success": request.query_params.get("success"),
        },
    )


@router.post("/teams")
async def create_team(
    request: Request,
    service: FromDishka[TeamService],
    name: str = Form(...),
    description: str = Form(""),
):
    user = get_web_user(request)
    if user is None:
        return RedirectResponse("/web/auth/login", status_code=303)
    try:
        team = await service.create_team(
            int(user["sub"]),
            CreateTeamRequest(name=name, description=description or None),
        )
        return RedirectResponse(f"/web/teams/{team.id}", status_code=303)
    except BaseError as e:
        return RedirectResponse(f"/web/dashboard?error={e.message}", status_code=303)


@router.post("/join")
async def join_team(
    request: Request,
    service: FromDishka[UserService],
    join_code: str = Form(...),
):
    user = get_web_user(request)
    if user is None:
        return RedirectResponse("/web/auth/login", status_code=303)
    try:
        await service.join_team(int(user["sub"]), join_code)
        return RedirectResponse("/web/dashboard?success=Вы+вступили+в+команду", status_code=303)
    except BaseError as e:
        return RedirectResponse(f"/web/dashboard?error={e.message}", status_code=303)
