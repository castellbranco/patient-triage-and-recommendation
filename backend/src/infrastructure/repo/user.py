"""
User Repository - Data access for User entity.
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models.user import User
from infrastructure.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User CRUD + custom queries."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        stmt = select(User).where(User.email == email)
        if hasattr(User, "deleted_at"):
            stmt = stmt.where(User.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_users(self) -> List[User]:
        """Get all active users."""
        stmt = select(User).where(User.is_active == True)
        if hasattr(User, "deleted_at"):
            stmt = stmt.where(User.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_role(self, role: str) -> List[User]:
        """Get all users with a specific role."""
        stmt = select(User).where(User.role == role)
        if hasattr(User, "deleted_at"):
            stmt = stmt.where(User.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
