"""
User Repository Module
"""

from sqlalchemy import select

from infrastructure.database.models.user import User
from infrastructure.repo.base import BaseRepository


class UserRepository(BaseRepository):

    model = User

    async def get_by_email(self, email: str):
        stmt = select(User).where(User.email == email, User.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_role(self, role: str):
        stmt = select(User).where(User.role == role, User.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def email_exists(self, email: str):
        return await self.get_by_email(email) is not None
