from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Request, Response, status

from apps.auth.schemas import LoginRequest, RegisterRequest, TokenResponse, UserMeResponse
from apps.auth.service import AuthService
from configs.settings import Settings

router = APIRouter(prefix="/auth", tags=["Auth"])
router.route_class = DishkaRoute


@router.post("/register", response_model=UserMeResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    service: FromDishka[AuthService],
) -> UserMeResponse:
    user = await service.register(body)
    return UserMeResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    response: Response,
    service: FromDishka[AuthService],
    settings: FromDishka[Settings],
) -> TokenResponse:
    access_token, refresh_token, expires_at = await service.login(body.email, body.password)
    cookie_params = settings.get_auth_cookie_params()
    response.set_cookie(
        key=settings.AUTH_REFRESH_COOKIE_NAME,
        value=refresh_token,
        path=settings.AUTH_REFRESH_COOKIE_PATH,
        httponly=True,
        expires=int(expires_at.timestamp()),
        **cookie_params,  # type: ignore[arg-type]
    )
    return TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request,
    service: FromDishka[AuthService],
    settings: FromDishka[Settings],
) -> TokenResponse:
    raw_token = request.cookies.get(settings.AUTH_REFRESH_COOKIE_NAME)
    if not raw_token:
        from fastapi import HTTPException

        raise HTTPException(status_code=401, detail="Refresh token missing")
    access_token = await service.refresh(raw_token)
    return TokenResponse(access_token=access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    service: FromDishka[AuthService],
    settings: FromDishka[Settings],
) -> None:
    raw_token = request.cookies.get(settings.AUTH_REFRESH_COOKIE_NAME)
    if raw_token:
        await service.logout(raw_token)
    response.delete_cookie(
        key=settings.AUTH_REFRESH_COOKIE_NAME,
        path=settings.AUTH_REFRESH_COOKIE_PATH,
    )
