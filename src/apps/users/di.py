from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from apps.users.repository import UserRepository
from apps.users.service import UserService
from packages.db.transaction import TransactionManager


class UsersProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def user_repository(self, session: AsyncSession) -> UserRepository:
        return UserRepository(session)

    @provide(scope=Scope.REQUEST)
    def user_service(
        self,
        user_repo: UserRepository,
        session: AsyncSession,
        tx: TransactionManager,
    ) -> UserService:
        return UserService(user_repo, session, tx)


provider = UsersProvider()
