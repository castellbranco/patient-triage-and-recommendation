"""
Provider Repository Module
"""

from uuid import UUID

from sqlalchemy import select

from infrastructure.database.models.provider import Provider
from infrastructure.repo.base import BaseRepository


class ProviderRepository(BaseRepository):

    model = Provider

    async def get_by_user_id(self, user_id: UUID):
        stmt = select(Provider).where(Provider.user_id == user_id, Provider.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_license(self, license_number: str):
        stmt = select(Provider).where(
            Provider.license_number == license_number, Provider.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def user_has_provider(self, user_id: UUID):
        return await self.get_by_user_id(user_id) is not None

    async def license_exists(self, license_number: str):
        return await self.get_by_license(license_number) is not None

    async def get_by_specialty(self, specialty: str):
        stmt = select(Provider).where(
            Provider.specialty == specialty, Provider.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_accepting_patients(self):
        stmt = select(Provider).where(
            Provider.accepting_new_patients == True, Provider.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
