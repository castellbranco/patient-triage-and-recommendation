"""
Patient Repository Module
"""

from uuid import UUID

from sqlalchemy import select

from infrastructure.database.models.patient import Patient
from infrastructure.repo.base import BaseRepository


class PatientRepository(BaseRepository):

    model = Patient

    async def get_by_user_id(self, user_id: UUID):
        stmt = select(Patient).where(Patient.user_id == user_id, Patient.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def user_has_patient(self, user_id: UUID):
        return await self.get_by_user_id(user_id) is not None
