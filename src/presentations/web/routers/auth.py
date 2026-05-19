from pathlib import Path

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from apps.auth.schemas import RegisterRequest
from apps.auth.service import AuthService, EmailAlreadyTakenError, InvalidCredentialsError
from configs import settings
from presentations.web.deps import get_web_user

router = APIRouter(tags=["Web:Auth"])
router.route_class = DishkaRoute

_templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


@router.get("/auth/login")
async def login_page(request: Request):
    if get_web_user(request):
        return RedirectResponse("/web/dashboard", status_code=303)
    return _templates.TemplateResponse(
        request,
        "auth/login.html",
        {
            "error": request.query_params.get("error"),
            "success": request.query_params.get("success"),
        },
    )


@router.post("/auth/login")
async def login_submit(
    request: Request,
    service: FromDishka[AuthService],
    email: str = Form(...),
    password: str = Form(...),
):
    try:
        access_token, refresh_token, expires_at = await service.login(email, password)
    except InvalidCredentialsError:
        return RedirectResponse("/web/auth/login?error=Неверный+email+или+пароль", status_code=303)

    resp = RedirectResponse("/web/dashboard", status_code=303)
    resp.set_cookie(
        key=settings.AUTH_ACCESS_COOKIE_NAME,
        value=access_token,
        httponly=True,
        path="/",
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )
    resp.set_cookie(
        key=settings.AUTH_REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        path=settings.AUTH_REFRESH_COOKIE_PATH,
        expires=int(expires_at.timestamp()),
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )
    return resp


@router.get("/auth/register")
async def register_page(request: Request):
    if get_web_user(request):
        return RedirectResponse("/web/dashboard", status_code=303)
    return _templates.TemplateResponse(
        request,
        "auth/register.html",
        {
            "error": request.query_params.get("error"),
        },
    )


@router.post("/auth/register")
async def register_submit(
    request: Request,
    service: FromDishka[AuthService],
    email: str = Form(...),
    password: str = Form(...),
    first_name: str = Form(""),
    last_name: str = Form(""),
):
    try:
        await service.register(
            RegisterRequest(
                email=email,
                password=password,
                first_name=first_name or None,
                last_name=last_name or None,
            )
        )
    except EmailAlreadyTakenError:
        return RedirectResponse("/web/auth/register?error=Email+уже+занят", status_code=303)
    except Exception:
        return RedirectResponse("/web/auth/register?error=Ошибка+регистрации", status_code=303)

    try:
        access_token, refresh_token, expires_at = await service.login(email, password)
    except Exception:
        return RedirectResponse("/web/auth/login?success=Аккаунт+создан", status_code=303)

    resp = RedirectResponse("/web/dashboard", status_code=303)
    resp.set_cookie(
        key=settings.AUTH_ACCESS_COOKIE_NAME,
        value=access_token,
        httponly=True,
        path="/",
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )
    resp.set_cookie(
        key=settings.AUTH_REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        path=settings.AUTH_REFRESH_COOKIE_PATH,
        expires=int(expires_at.timestamp()),
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )
    return resp


@router.post("/auth/logout")
async def logout(request: Request, service: FromDishka[AuthService]):
    raw_token = request.cookies.get(settings.AUTH_REFRESH_COOKIE_NAME)
    if raw_token:
        try:
            await service.logout(raw_token)
        except Exception:
            pass
    resp = RedirectResponse("/web/auth/login", status_code=303)
    resp.delete_cookie(settings.AUTH_ACCESS_COOKIE_NAME)
    resp.delete_cookie(settings.AUTH_REFRESH_COOKIE_NAME, path=settings.AUTH_REFRESH_COOKIE_PATH)
    return resp
