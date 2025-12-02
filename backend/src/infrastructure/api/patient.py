"""
Patient API Module - Routes for patient endpoints
"""

from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from infrastructure.api.utils import Pagination, PatientServiceDep
from infrastructure.database.schemas.patient import (
    PatientListResponse,
    PatientRegister,
    PatientResponse,
    PatientUpdate,
)


router = APIRouter(prefix="/patients", tags=["Patients"], route_class=DishkaRoute)


@router.post(
    "/register",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register patient",
    responses={
        201: {"description": "Patient registered successfully"},
        409: {"description": "Email already registered"},
    },
)
async def register_patient(
    data: PatientRegister, service: PatientServiceDep
) -> PatientResponse:
    """Register a new patient (creates User + Patient in one call)."""
    patient = await service.register_patient(data)
    return PatientResponse.model_validate(patient)


@router.get(
    "",
    response_model=PatientListResponse,
    summary="List patients",
    responses={200: {"description": "Patients retrieved"}},
)
async def list_patients(
    service: PatientServiceDep, pagination: Pagination
) -> PatientListResponse:
    """List all patients with pagination."""
    patients = await service.list_patients(skip=pagination.skip, limit=pagination.limit)
    total = await service.count_patients()

    return PatientListResponse(
        patients=[PatientResponse.model_validate(p) for p in patients],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Get patient",
    responses={
        200: {"description": "Patient retrieved"},
        404: {"description": "Patient not found"},
    },
)
async def get_patient(patient_id: UUID, service: PatientServiceDep) -> PatientResponse:
    """Get a patient by ID."""
    patient = await service.get_patient_or_raise(patient_id)
    return PatientResponse.model_validate(patient)


@router.patch(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Update patient",
    responses={
        200: {"description": "Patient updated"},
        404: {"description": "Patient not found"},
    },
)
async def update_patient(
    patient_id: UUID, data: PatientUpdate, service: PatientServiceDep
) -> PatientResponse:
    """Update a patient's profile. Only provided fields are updated."""
    patient = await service.update_patient(patient_id, data)
    return PatientResponse.model_validate(patient)


@router.delete(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Delete patient",
    responses={
        200: {"description": "Patient deleted"},
        404: {"description": "Patient not found"},
    },
)
async def delete_patient(
    patient_id: UUID, service: PatientServiceDep
) -> PatientResponse:
    """Soft-delete a patient (data retained for audit)."""
    patient = await service.delete_patient(patient_id)
    return PatientResponse.model_validate(patient)
