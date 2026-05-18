import secrets
from datetime import UTC, datetime, timedelta

from apps.auth.models import RefreshToken
from apps.auth.repository import RefreshTokenRepository, UserRepository
from apps.auth.schemas import RegisterRequest
from apps.users.models import User
from configs.settings import Settings
from packages.db.transaction import TransactionManager
from packages.errors import BaseError
from packages.security import PasswordHasher
from packages.security.jwt import JwtManager, JwtTokenPayload


class EmailAlreadyTakenError(BaseError):
    code = "unique"
    message = "Email already registered"
    status_code = 409


class InvalidCredentialsError(BaseError):
    code = "invalid_credentials"
    message = "Invalid email or password"
    status_code = 401


class InvalidRefreshTokenError(BaseError):
    code = "invalid_credentials"
    message = "Invalid or expired refresh token"
    status_code = 401


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        token_repo: RefreshTokenRepository,
        password_hasher: PasswordHasher,
        jwt_manager: JwtManager,
        tx: TransactionManager,
        settings: Settings,
    ) -> None:
        self._user_repo = user_repo
        self._token_repo = token_repo
        self._hasher = password_hasher
        self._jwt = jwt_manager
        self._tx = tx
        self._access_ttl = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRES_MINUTES)
        self._refresh_ttl = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRES_DAYS)

    async def register(self, data: RegisterRequest) -> User:
        if await self._user_repo.get_by_email(data.email):
            raise EmailAlreadyTakenError()
        user = User(
            email=data.email,
            password_hash=self._hasher.hash(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
        )
        async with self._tx:
            await self._user_repo.add(user)
        return user

    async def login(self, email: str, password: str) -> tuple[str, str, datetime]:
        user = await self._user_repo.get_by_email(email)
        if not user or not self._hasher.verify(password, user.password_hash):
            raise InvalidCredentialsError()
        if not user.is_active:
            raise InvalidCredentialsError()

        access_token = self._jwt.encode(
            JwtTokenPayload(sub=str(user.id), type="access"),
            ttl=self._access_ttl,
        )

        raw_refresh = secrets.token_hex(32)
        token_hash = self._token_repo.hash_token(raw_refresh)
        expires_at = datetime.now(UTC) + self._refresh_ttl

        async with self._tx:
            await self._token_repo.add(
                RefreshToken(
                    user_id=user.id,
                    token_hash=token_hash,
                    expires_at=expires_at,
                )
            )

        return access_token, raw_refresh, expires_at

    async def refresh(self, raw_refresh_token: str) -> str:
        token_hash = self._token_repo.hash_token(raw_refresh_token)
        token = await self._token_repo.get_by_hash(token_hash)
        if not token or token.expires_at < datetime.now(UTC):
            raise InvalidRefreshTokenError()

        return self._jwt.encode(
            JwtTokenPayload(sub=str(token.user_id), type="access"),
            ttl=self._access_ttl,
        )

    async def logout(self, raw_refresh_token: str) -> None:
        token_hash = self._token_repo.hash_token(raw_refresh_token)
        async with self._tx:
            await self._token_repo.revoke_by_hash(token_hash)
