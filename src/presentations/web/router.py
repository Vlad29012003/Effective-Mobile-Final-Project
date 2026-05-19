from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from presentations.web.routers.auth import router as auth_router
from presentations.web.routers.calendar import router as calendar_router
from presentations.web.routers.dashboard import router as dashboard_router
from presentations.web.routers.teams import router as teams_router

web_router = APIRouter(prefix="/web")
web_router.include_router(auth_router)
web_router.include_router(dashboard_router)
web_router.include_router(teams_router)
web_router.include_router(calendar_router)


@web_router.get("/")
async def web_root():
    return RedirectResponse("/web/dashboard", status_code=303)


STATIC_DIR = Path(__file__).parent / "static"
