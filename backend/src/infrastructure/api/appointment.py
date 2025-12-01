"""
Appointment API Module - Routes for appointment endpoints
"""

from uuid import UUID

from fastapi import APIRouter, status

from infrastructure.api.utils import (
    Pagination,
    AppointmentServiceDep,
    bad_request_exception,
    not_found_exception,
)
from infrastructure.database.schemas.appointment import (
    AppointmentCreate,
    AppointmentListResponse,
    AppointmentResponse,
    AppointmentUpdate,
)
from services.errors import (
    AppointmentConflictError,
    AppointmentInPastError,
    AppointmentNotFoundError,
    InvalidAppointmentStatusError,
    PatientNotFoundError,
    ProviderNotAcceptingPatientsError,
    ProviderNotFoundError,
)


router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create appointment",
    responses={
        201: {"description": "Appointment created"},
        400: {"description": "Invalid data or conflict"},
        404: {"description": "Patient or provider not found"},
    },
)
async def create_appointment(
    data: AppointmentCreate, service: AppointmentServiceDep
) -> AppointmentResponse:
    """Create a new appointment."""
    try:
        appointment = await service.create_appointment(data)
        return AppointmentResponse.model_validate(appointment)
    except PatientNotFoundError:
        raise not_found_exception("Patient", str(data.patient_id))
    except ProviderNotFoundError:
        raise not_found_exception("Provider", str(data.provider_id))
    except ProviderNotAcceptingPatientsError:
        raise bad_request_exception("Provider is not accepting new patients")
    except AppointmentInPastError:
        raise bad_request_exception("Cannot schedule appointment in the past")
    except AppointmentConflictError:
        raise bad_request_exception("Provider has a scheduling conflict at this time")


@router.get(
    "",
    response_model=AppointmentListResponse,
    summary="List appointments",
    responses={200: {"description": "Appointments retrieved"}},
)
async def list_appointments(
    service: AppointmentServiceDep, pagination: Pagination
) -> AppointmentListResponse:
    """List all appointments with pagination."""
    appointments = await service.list_appointments(
        skip=pagination.skip, limit=pagination.limit
    )
    total = await service.count_appointments()

    return AppointmentListResponse(
        appointments=[AppointmentResponse.model_validate(a) for a in appointments],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Get appointment",
    responses={
        200: {"description": "Appointment retrieved"},
        404: {"description": "Appointment not found"},
    },
)
async def get_appointment(
    appointment_id: UUID, service: AppointmentServiceDep
) -> AppointmentResponse:
    """Get an appointment by ID."""
    try:
        appointment = await service.get_appointment_or_raise(appointment_id)
        return AppointmentResponse.model_validate(appointment)
    except AppointmentNotFoundError:
        raise not_found_exception("Appointment", str(appointment_id))


@router.patch(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Update appointment",
    responses={
        200: {"description": "Appointment updated"},
        400: {"description": "Invalid status transition or conflict"},
        404: {"description": "Appointment not found"},
    },
)
async def update_appointment(
    appointment_id: UUID, data: AppointmentUpdate, service: AppointmentServiceDep
) -> AppointmentResponse:
    """
    Update an appointment. Only provided fields are updated.
    
    Status transitions:
    - scheduled → confirmed, cancelled
    - confirmed → completed, cancelled, no_show
    
    To cancel, include: {"status": "cancelled", "canceled_by_and_why": {...}}
    """
    try:
        appointment = await service.update_appointment(appointment_id, data)
        return AppointmentResponse.model_validate(appointment)
    except AppointmentNotFoundError:
        raise not_found_exception("Appointment", str(appointment_id))
    except InvalidAppointmentStatusError as e:
        raise bad_request_exception(str(e))
    except AppointmentInPastError:
        raise bad_request_exception("Cannot reschedule to a past datetime")
    except AppointmentConflictError:
        raise bad_request_exception("Provider has a scheduling conflict at this time")


@router.delete(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Delete appointment",
    responses={
        200: {"description": "Appointment deleted"},
        404: {"description": "Appointment not found"},
    },
)
async def delete_appointment(
    appointment_id: UUID, service: AppointmentServiceDep
) -> AppointmentResponse:
    """Soft-delete an appointment."""
    try:
        appointment = await service.delete_appointment(appointment_id)
        return AppointmentResponse.model_validate(appointment)
    except AppointmentNotFoundError:
        raise not_found_exception("Appointment", str(appointment_id))
