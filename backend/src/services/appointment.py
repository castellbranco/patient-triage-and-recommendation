"""
Appointment Service Module
"""

from datetime import datetime
from uuid import UUID

from infrastructure.database.models.appointment import Appointment
from infrastructure.database.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    CancellationSchema,
)
from infrastructure.repo.appointment import AppointmentRepository
from services.errors import (
    AppointmentNotFoundError,
    AppointmentConflictError,
    AppointmentInPastError,
    InvalidAppointmentStatusError,
    ProviderNotFoundError,
    PatientNotFoundError,
    ProviderNotAcceptingPatientsError,
)


# Valid status transitions
STATUS_TRANSITIONS = {
    "scheduled": ["confirmed", "cancelled"],
    "confirmed": ["completed", "cancelled", "no_show"],
    "completed": [],
    "cancelled": [],
    "no_show": [],
}


class AppointmentService:

    def __init__(
        self,
        repository: AppointmentRepository,
        patient_repository,
        provider_repository,
    ):
        self.repository = repository
        self.patient_repository = patient_repository
        self.provider_repository = provider_repository

    async def create_appointment(self, data: AppointmentCreate):
        """Create a new appointment with all validations"""
        # Validate datetime is not in the past
        if data.appointment_datetime < datetime.utcnow():
            raise AppointmentInPastError()

        # Validate patient exists
        patient = await self.patient_repository.get_by_id(data.patient_id)
        if not patient:
            raise PatientNotFoundError(str(data.patient_id))

        # Validate provider exists and is accepting patients
        provider = await self.provider_repository.get_by_id(data.provider_id)
        if not provider:
            raise ProviderNotFoundError(str(data.provider_id))
        if not provider.accepting_new_patients:
            raise ProviderNotAcceptingPatientsError(str(data.provider_id))

        # Check for scheduling conflicts
        if await self.repository.check_conflict(data.provider_id, data.appointment_datetime):
            raise AppointmentConflictError(
                str(data.provider_id), data.appointment_datetime.isoformat()
            )

        appointment = Appointment(
            patient_id=data.patient_id,
            provider_id=data.provider_id,
            appointment_datetime=data.appointment_datetime,
            duration=data.duration,
            type=data.type,
            chief_complaint=data.chief_complaint,
            notes=data.notes,
            symptoms=[s.model_dump() for s in data.symptoms],
            status="scheduled",
        )

        return await self.repository.create(appointment)

    async def get_appointment(self, appointment_id: UUID):
        return await self.repository.get_by_id(appointment_id)

    async def get_appointment_or_raise(self, appointment_id: UUID):
        appointment = await self.repository.get_by_id(appointment_id)
        if not appointment:
            raise AppointmentNotFoundError(str(appointment_id))
        return appointment

    async def update_appointment(self, appointment_id: UUID, data: AppointmentUpdate):
        appointment = await self.get_appointment_or_raise(appointment_id)

        # Handle status change with validation
        if data.status is not None and data.status != appointment.status:
            if data.status not in STATUS_TRANSITIONS.get(appointment.status, []):
                raise InvalidAppointmentStatusError(appointment.status, data.status)
            appointment.status = data.status

        # Handle datetime change with conflict check
        if data.appointment_datetime is not None:
            if data.appointment_datetime < datetime.utcnow():
                raise AppointmentInPastError()
            if data.appointment_datetime != appointment.appointment_datetime:
                if await self.repository.check_conflict(
                    appointment.provider_id, data.appointment_datetime
                ):
                    raise AppointmentConflictError(
                        str(appointment.provider_id), data.appointment_datetime.isoformat()
                    )
                appointment.appointment_datetime = data.appointment_datetime

        if data.duration is not None:
            appointment.duration = data.duration
        if data.type is not None:
            appointment.type = data.type
        if data.chief_complaint is not None:
            appointment.chief_complaint = data.chief_complaint
        if data.notes is not None:
            appointment.notes = data.notes
        if data.symptoms is not None:
            appointment.symptoms = [s.model_dump() for s in data.symptoms]
        if data.diagnosis is not None:
            appointment.diagnosis = [d.model_dump() for d in data.diagnosis]
        if data.canceled_by_and_why is not None:
            appointment.canceled_by_and_why = data.canceled_by_and_why.model_dump()

        return await self.repository.update(appointment)

    async def cancel_appointment(
        self, appointment_id: UUID, canceled_by: str, reason: str | None = None
    ):
        """Cancel an appointment with cancellation details"""
        appointment = await self.get_appointment_or_raise(appointment_id)

        if "cancelled" not in STATUS_TRANSITIONS.get(appointment.status, []):
            raise InvalidAppointmentStatusError(appointment.status, "cancelled")

        appointment.status = "cancelled"
        appointment.canceled_by_and_why = CancellationSchema(
            canceled_by=canceled_by, reason=reason
        ).model_dump()

        return await self.repository.update(appointment)

    async def confirm_appointment(self, appointment_id: UUID):
        """Confirm a scheduled appointment"""
        appointment = await self.get_appointment_or_raise(appointment_id)

        if "confirmed" not in STATUS_TRANSITIONS.get(appointment.status, []):
            raise InvalidAppointmentStatusError(appointment.status, "confirmed")

        appointment.status = "confirmed"
        return await self.repository.update(appointment)

    async def complete_appointment(self, appointment_id: UUID):
        """Mark appointment as completed"""
        appointment = await self.get_appointment_or_raise(appointment_id)

        if "completed" not in STATUS_TRANSITIONS.get(appointment.status, []):
            raise InvalidAppointmentStatusError(appointment.status, "completed")

        appointment.status = "completed"
        return await self.repository.update(appointment)

    async def mark_no_show(self, appointment_id: UUID):
        """Mark patient as no-show"""
        appointment = await self.get_appointment_or_raise(appointment_id)

        if "no_show" not in STATUS_TRANSITIONS.get(appointment.status, []):
            raise InvalidAppointmentStatusError(appointment.status, "no_show")

        appointment.status = "no_show"
        return await self.repository.update(appointment)

    async def delete_appointment(self, appointment_id: UUID):
        appointment = await self.get_appointment_or_raise(appointment_id)
        return await self.repository.soft_delete(appointment)

    async def list_appointments(self, skip: int = 0, limit: int = 100):
        return await self.repository.get_all(skip=skip, limit=limit)

    async def list_by_patient(self, patient_id: UUID):
        return await self.repository.get_by_patient_id(patient_id)

    async def list_by_provider(self, provider_id: UUID):
        return await self.repository.get_by_provider_id(provider_id)

    async def list_upcoming_for_patient(self, patient_id: UUID):
        return await self.repository.get_upcoming_for_patient(patient_id)

    async def list_upcoming_for_provider(self, provider_id: UUID):
        return await self.repository.get_upcoming_for_provider(provider_id)

    async def get_provider_schedule(self, provider_id: UUID, start: datetime, end: datetime):
        return await self.repository.get_provider_appointments_in_range(provider_id, start, end)

    async def count_appointments(self):
        return await self.repository.count()
