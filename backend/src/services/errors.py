"""
Service Errors Module
"""

from fastapi import status


class ServiceError(Exception):
    """Base class for all service-layer errors with HTTP status mapping."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str = "Service error occurred"):
        self.message = message
        super().__init__(self.message)


class NotFoundError(ServiceError):
    """Base class for all 'not found' errors."""

    status_code = status.HTTP_404_NOT_FOUND


class UserNotFoundError(NotFoundError):
    def __init__(self, identifier: str):
        super().__init__(f"User {identifier} not found")


class PatientNotFoundError(NotFoundError):
    def __init__(self, identifier: str):
        super().__init__(f"Patient {identifier} not found")


class ProviderNotFoundError(NotFoundError):
    def __init__(self, identifier: str):
        super().__init__(f"Provider {identifier} not found")


class AppointmentNotFoundError(NotFoundError):
    def __init__(self, identifier: str):
        super().__init__(f"Appointment {identifier} not found")


class ConflictError(ServiceError):
    """Base class for all conflict/duplicate errors."""

    status_code = status.HTTP_409_CONFLICT


class EmailAlreadyExistsError(ConflictError):
    def __init__(self, email: str):
        super().__init__(f"Email '{email}' is already registered")


class PatientAlreadyExistsError(ConflictError):
    def __init__(self, user_id: str):
        super().__init__(f"Patient profile already exists for user {user_id}")


class ProviderAlreadyExistsError(ConflictError):
    def __init__(self, user_id: str):
        super().__init__(f"Provider profile already exists for user {user_id}")


class LicenseAlreadyExistsError(ConflictError):
    def __init__(self, license_number: str):
        super().__init__(f"License number '{license_number}' is already registered")


class AppointmentConflictError(ConflictError):
    def __init__(self, provider_id: str, datetime_str: str):
        super().__init__(f"Provider {provider_id} already has appointment at {datetime_str}")


class BadRequestError(ServiceError):
    """Base class for all validation/bad request errors."""

    status_code = status.HTTP_400_BAD_REQUEST


class InvalidAppointmentStatusError(BadRequestError):
    def __init__(self, current_status: str, target_status: str):
        super().__init__(f"Cannot change status from '{current_status}' to '{target_status}'")


class AppointmentInPastError(BadRequestError):
    def __init__(self):
        super().__init__("Cannot schedule appointment in the past")


class ProviderNotAcceptingPatientsError(BadRequestError):
    def __init__(self, identifier: str):
        super().__init__(f"Provider {identifier} is not accepting new patients")


class UnauthorizedError(ServiceError):
    """Base class for authentication errors."""

    status_code = status.HTTP_401_UNAUTHORIZED


class InvalidCredentialsError(UnauthorizedError):
    def __init__(self):
        super().__init__("Invalid email or password")


class UserNotActiveError(UnauthorizedError):
    def __init__(self, identifier: str):
        super().__init__(f"User {identifier} is not active")


UserServiceError = ServiceError
PatientServiceError = ServiceError
ProviderServiceError = ServiceError
AppointmentServiceError = ServiceError
