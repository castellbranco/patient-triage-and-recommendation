"""
Service Errors Module
"""


class ServiceError(Exception):
    def __init__(self, message: str = "Service error occurred"):
        self.message = message
        super().__init__(self.message)

class UserServiceError(ServiceError):
    pass


class EmailAlreadyExistsError(UserServiceError):
    def __init__(self, email: str):
        super().__init__(f"Email {email} already registered")


class UserNotFoundError(UserServiceError):
    def __init__(self, identifier: str):
        super().__init__(f"User {identifier} not found")


class InvalidCredentialsError(UserServiceError):
    def __init__(self):
        super().__init__("Invalid email or password")


class UserNotActiveError(UserServiceError):
    def __init__(self, identifier: str):
        super().__init__(f"User {identifier} is not active")


class PatientServiceError(ServiceError):
    pass


class PatientNotFoundError(PatientServiceError):
    def __init__(self, identifier: str):
        super().__init__(f"Patient {identifier} not found")


class PatientAlreadyExistsError(PatientServiceError):
    def __init__(self, user_id: str):
        super().__init__(f"Patient profile already exists for user {user_id}")


class ProviderServiceError(ServiceError):
    pass


class ProviderNotFoundError(ProviderServiceError):
    def __init__(self, identifier: str):
        super().__init__(f"Provider {identifier} not found")


class ProviderAlreadyExistsError(ProviderServiceError):
    def __init__(self, user_id: str):
        super().__init__(f"Provider profile already exists for user {user_id}")


class LicenseAlreadyExistsError(ProviderServiceError):
    def __init__(self, license_number: str):
        super().__init__(f"License number {license_number} already registered")


class ProviderNotAcceptingPatientsError(ProviderServiceError):
    def __init__(self, identifier: str):
        super().__init__(f"Provider {identifier} is not accepting new patients")


class AppointmentServiceError(ServiceError):
    pass


class AppointmentNotFoundError(AppointmentServiceError):
    def __init__(self, identifier: str):
        super().__init__(f"Appointment {identifier} not found")


class AppointmentConflictError(AppointmentServiceError):
    def __init__(self, provider_id: str, datetime_str: str):
        super().__init__(f"Provider {provider_id} already has appointment at {datetime_str}")


class InvalidAppointmentStatusError(AppointmentServiceError):
    def __init__(self, current_status: str, target_status: str):
        super().__init__(f"Cannot change status from {current_status} to {target_status}")


class AppointmentInPastError(AppointmentServiceError):
    def __init__(self):
        super().__init__("Cannot schedule appointment in the past")
