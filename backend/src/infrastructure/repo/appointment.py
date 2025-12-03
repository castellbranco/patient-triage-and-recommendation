"""
Appointment Repository Module
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select, and_

from infrastructure.database.models.appointment import Appointment
from infrastructure.repo.base import BaseRepository


class AppointmentRepository(BaseRepository):

    model = Appointment

    async def get_by_patient_id(self, patient_id: UUID):
        stmt = (
            select(Appointment)
            .where(Appointment.patient_id == patient_id, Appointment.deleted_at.is_(None))
            .order_by(Appointment.appointment_datetime.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_provider_id(self, provider_id: UUID):
        stmt = (
            select(Appointment)
            .where(Appointment.provider_id == provider_id, Appointment.deleted_at.is_(None))
            .order_by(Appointment.appointment_datetime.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_status(self, status: str):
        stmt = (
            select(Appointment)
            .where(Appointment.status == status, Appointment.deleted_at.is_(None))
            .order_by(Appointment.appointment_datetime.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_provider_appointments_in_range(
        self, provider_id: UUID, start: datetime, end: datetime
    ):
        stmt = (
            select(Appointment)
            .where(
                and_(
                    Appointment.provider_id == provider_id,
                    Appointment.appointment_datetime >= start,
                    Appointment.appointment_datetime < end,
                    Appointment.deleted_at.is_(None),
                    Appointment.status.notin_(["cancelled", "no_show"]),
                )
            )
            .order_by(Appointment.appointment_datetime)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def check_conflict(self, provider_id: UUID, appointment_datetime: datetime):
        """Check if provider has an existing appointment at the given time"""
        stmt = select(Appointment).where(
            and_(
                Appointment.provider_id == provider_id,
                Appointment.appointment_datetime == appointment_datetime,
                Appointment.deleted_at.is_(None),
                Appointment.status.notin_(["cancelled", "no_show"]),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_upcoming_for_patient(
        self, patient_id: UUID, from_datetime: datetime | None = None
    ):
        if from_datetime is None:
            from_datetime = datetime.utcnow()

        stmt = (
            select(Appointment)
            .where(
                and_(
                    Appointment.patient_id == patient_id,
                    Appointment.appointment_datetime >= from_datetime,
                    Appointment.deleted_at.is_(None),
                    Appointment.status.in_(["scheduled", "confirmed"]),
                )
            )
            .order_by(Appointment.appointment_datetime)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_upcoming_for_provider(
        self, provider_id: UUID, from_datetime: datetime | None = None
    ):
        if from_datetime is None:
            from_datetime = datetime.utcnow()

        stmt = (
            select(Appointment)
            .where(
                and_(
                    Appointment.provider_id == provider_id,
                    Appointment.appointment_datetime >= from_datetime,
                    Appointment.deleted_at.is_(None),
                    Appointment.status.in_(["scheduled", "confirmed"]),
                )
            )
            .order_by(Appointment.appointment_datetime)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
