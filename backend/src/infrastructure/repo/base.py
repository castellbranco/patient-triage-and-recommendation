"""
Base Repository Module
"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:

    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entity):
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def get_by_id(self, entity_id: UUID):
        stmt = select(self.model).where(self.model.id == entity_id, self.model.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100):
        stmt = select(self.model).where(self.model.deleted_at.is_(None)).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, entity):
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity):
        await self.session.delete(entity)
        await self.session.flush()

    async def soft_delete(self, entity):
        entity.deleted_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def count(self):
        stmt = select(func.count()).select_from(self.model).where(self.model.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def exists(self, entity_id: UUID):
        return await self.get_by_id(entity_id) is not None