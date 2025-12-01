"""
Services Package
"""

from services.user import UserService
from services.patient import PatientService

from services.errors import (
    ServiceError,
    UserServiceError,
    EmailAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError,
    UserNotActiveError,
    PatientServiceError,
    PatientNotFoundError,
    PatientAlreadyExistsError,
    ProviderServiceError,
    ProviderNotFoundError,
    ProviderAlreadyExistsError,
    LicenseAlreadyExistsError,
    ProviderNotAcceptingPatientsError,
    AppointmentServiceError,
    AppointmentNotFoundError,
    AppointmentConflictError,
    InvalidAppointmentStatusError,
    AppointmentInPastError,
)

__all__ = [
    "UserService",
    "PatientService",
    "ServiceError",
    "UserServiceError",
    "EmailAlreadyExistsError",
    "UserNotFoundError",
    "InvalidCredentialsError",
    "UserNotActiveError",
    "PatientServiceError",
    "PatientNotFoundError",
    "PatientAlreadyExistsError",
    "ProviderServiceError",
    "ProviderNotFoundError",
    "ProviderAlreadyExistsError",
    "LicenseAlreadyExistsError",
    "ProviderNotAcceptingPatientsError",
    "AppointmentServiceError",
    "AppointmentNotFoundError",
    "AppointmentConflictError",
    "InvalidAppointmentStatusError",
    "AppointmentInPastError",
]