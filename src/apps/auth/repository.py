import hashlib

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.auth.models import RefreshToken
from apps.users.models import User
from packages.db.repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, RefreshToken)

    @staticmethod
    def hash_token(raw: str) -> str:
        return hashlib.sha256(raw.encode()).hexdigest()

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        result = await self._session.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.is_revoked.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def revoke_by_hash(self, token_hash: str) -> None:
        await self._session.execute(
            update(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .values(is_revoked=True)
        )
