from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from apps.auth.repository import RefreshTokenRepository, UserRepository
from apps.auth.service import AuthService
from configs.settings import Settings
from packages.db.transaction import TransactionManager
from packages.security import PasswordHasher
from packages.security.jwt import JwtManager


class AuthProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def user_repository(self, session: AsyncSession) -> UserRepository:
        return UserRepository(session)

    @provide(scope=Scope.REQUEST)
    def refresh_token_repository(self, session: AsyncSession) -> RefreshTokenRepository:
        return RefreshTokenRepository(session)

    @provide(scope=Scope.REQUEST)
    def auth_service(
        self,
        user_repo: UserRepository,
        token_repo: RefreshTokenRepository,
        password_hasher: PasswordHasher,
        jwt_manager: JwtManager,
        tx: TransactionManager,
        settings: Settings,
    ) -> AuthService:
        return AuthService(user_repo, token_repo, password_hasher, jwt_manager, tx, settings)


provider = AuthProvider()
