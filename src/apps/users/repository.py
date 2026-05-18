from sqlalchemy.ext.asyncio import AsyncSession

from apps.users.models import User
from packages.db.repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self._session.get(User, user_id)
        return result
