"""
API Utilities Module - Shared dependencies and helpers for all routes.
"""

from typing import Annotated

from dishka.integrations.fastapi import FromDishka
from fastapi import Depends, HTTPException, Query, status

from services.user import UserService
from services.patient import PatientService
from services.provider import ProviderService
from services.appointment import AppointmentService


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


UserServiceDep = Annotated[UserService, FromDishka()]
PatientServiceDep = Annotated[PatientService, FromDishka()]
ProviderServiceDep = Annotated[ProviderService, FromDishka()]
AppointmentServiceDep = Annotated[AppointmentService, FromDishka()]


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
