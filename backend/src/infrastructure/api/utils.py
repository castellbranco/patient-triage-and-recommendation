"""
API Utilities Module - Shared dependencies and helpers for all routes.

This module centralizes reusable FastAPI dependencies, exception handlers,
and utility functions used across all API endpoints.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Query, status

class PaginationParams:
    """
    Dependency for pagination parameters.
    """

    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number (1-indexed)"),
        page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    ):
        self.page = page
        self.page_size = page_size
        self.skip = (page - 1) * page_size
        self.limit = page_size

Pagination = Annotated[PaginationParams, Depends()]


def not_found_exception(resource: str, identifier: str) -> HTTPException:
    """
    Create a 404 Not Found exception.
    """
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource} with id '{identifier}' not found",
    )


def conflict_exception(field: str, value: str) -> HTTPException:
    """
    Create a 409 Conflict exception.
    """
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"{field} '{value}' is already registered",
    )


def bad_request_exception(message: str) -> HTTPException:
    """
    Create a 400 Bad Request exception.
    """
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message,
    )


def forbidden_exception(message: str = "You don't have permission to perform this action") -> HTTPException:
    """
    Create a 403 Forbidden exception.
    """
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=message,
    )


def unauthorized_exception(message: str = "Invalid credentials") -> HTTPException:
    """
    Create a 401 Unauthorized exception.
    """
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
        headers={"WWW-Authenticate": "Bearer"},
    )


# =============================================================================
# Service Dependencies (Temporary - will be replaced with Dishka)
# =============================================================================
# These are placeholder dependencies that will be replaced with Dishka's
# FromDishka[ServiceType] once the DI container is fully configured.

from services.user import UserService
from services.patient import PatientService
from services.provider import ProviderService
from services.appointment import AppointmentService


# Service instance holders
_user_service_instance: UserService | None = None
_patient_service_instance: PatientService | None = None
_provider_service_instance: ProviderService | None = None
_appointment_service_instance: AppointmentService | None = None


def get_user_service() -> UserService:
    """
    Dependency that provides the UserService instance.

    TODO: Replace with Dishka's FromDishka[UserService] once DI is configured.
    """
    if _user_service_instance is None:
        raise RuntimeError(
            "UserService not configured. "
            "Call configure_services() or setup Dishka container."
        )
    return _user_service_instance


def get_patient_service() -> PatientService:
    """
    Dependency that provides the PatientService instance.

    TODO: Replace with Dishka's FromDishka[PatientService] once DI is configured.
    """
    if _patient_service_instance is None:
        raise RuntimeError(
            "PatientService not configured. "
            "Call configure_services() or setup Dishka container."
        )
    return _patient_service_instance


def get_provider_service() -> ProviderService:
    """
    Dependency that provides the ProviderService instance.

    TODO: Replace with Dishka's FromDishka[ProviderService] once DI is configured.
    """
    if _provider_service_instance is None:
        raise RuntimeError(
            "ProviderService not configured. "
            "Call configure_services() or setup Dishka container."
        )
    return _provider_service_instance


def get_appointment_service() -> AppointmentService:
    """
    Dependency that provides the AppointmentService instance.

    TODO: Replace with Dishka's FromDishka[AppointmentService] once DI is configured.
    """
    if _appointment_service_instance is None:
        raise RuntimeError(
            "AppointmentService not configured. "
            "Call configure_services() or setup Dishka container."
        )
    return _appointment_service_instance


def configure_services(
    user_service: UserService | None = None,
    patient_service: PatientService | None = None,
    provider_service: ProviderService | None = None,
    appointment_service: AppointmentService | None = None,
) -> None:
    """
    Configure service instances for dependency injection.
    """
    global _user_service_instance, _patient_service_instance
    global _provider_service_instance, _appointment_service_instance

    if user_service is not None:
        _user_service_instance = user_service
    if patient_service is not None:
        _patient_service_instance = patient_service
    if provider_service is not None:
        _provider_service_instance = provider_service
    if appointment_service is not None:
        _appointment_service_instance = appointment_service


# Type aliases for cleaner route signatures
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
PatientServiceDep = Annotated[PatientService, Depends(get_patient_service)]
ProviderServiceDep = Annotated[ProviderService, Depends(get_provider_service)]
AppointmentServiceDep = Annotated[AppointmentService, Depends(get_appointment_service)]
