"""
Provider Service Module
"""

from uuid import UUID

from infrastructure.database.models.provider import Provider
from infrastructure.database.schemas.provider import (
    ProviderCreate,
    ProviderRegister,
    ProviderUpdate,
)
from infrastructure.database.schemas.user import UserCreate
from infrastructure.repo.provider import ProviderRepository
from services.user import UserService
from services.errors import (
    ProviderNotFoundError,
    ProviderAlreadyExistsError,
    LicenseAlreadyExistsError,
)


class ProviderService:

    def __init__(self, repository: ProviderRepository, user_service: UserService):
        self.repository = repository
        self.user_service = user_service

    async def register_provider(self, data: ProviderRegister):
        """Full registration: creates User + Provider in one call"""
        if await self.repository.license_exists(data.license_number):
            raise LicenseAlreadyExistsError(data.license_number)

        user_data = UserCreate(
            email=data.email,
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name,
            phone_number=data.phone_number,
        )
        user = await self.user_service.create_user(user_data, role="provider")

        provider = Provider(
            user_id=user.id,
            specialty=data.specialty,
            license_number=data.license_number,
            credentials=data.credentials,
            years_of_experience=data.years_of_experience,
            accepting_new_patients=data.accepting_new_patients,
            languages_spoken=data.languages_spoken,
            accepted_insurances=data.accepted_insurances,
            certifications=data.certifications,
        )

        return await self.repository.create(provider)

    async def create_provider(self, data: ProviderCreate):
        """Create provider for existing user"""
        if await self.repository.user_has_provider(data.user_id):
            raise ProviderAlreadyExistsError(str(data.user_id))

        if await self.repository.license_exists(data.license_number):
            raise LicenseAlreadyExistsError(data.license_number)

        provider = Provider(
            user_id=data.user_id,
            specialty=data.specialty,
            license_number=data.license_number,
            credentials=data.credentials,
            years_of_experience=data.years_of_experience,
            accepting_new_patients=data.accepting_new_patients,
            languages_spoken=data.languages_spoken,
            accepted_insurances=data.accepted_insurances,
            certifications=data.certifications,
        )

        return await self.repository.create(provider)

    async def get_provider(self, provider_id: UUID):
        return await self.repository.get_by_id(provider_id)

    async def get_provider_or_raise(self, provider_id: UUID):
        provider = await self.repository.get_by_id(provider_id)
        if not provider:
            raise ProviderNotFoundError(str(provider_id))
        return provider

    async def get_provider_by_user_id(self, user_id: UUID):
        return await self.repository.get_by_user_id(user_id)

    async def get_provider_by_license(self, license_number: str):
        return await self.repository.get_by_license(license_number)

    async def update_provider(self, provider_id: UUID, data: ProviderUpdate):
        provider = await self.get_provider_or_raise(provider_id)

        # Check license uniqueness if changing
        if data.license_number is not None and data.license_number != provider.license_number:
            if await self.repository.license_exists(data.license_number):
                raise LicenseAlreadyExistsError(data.license_number)
            provider.license_number = data.license_number

        if data.specialty is not None:
            provider.specialty = data.specialty
        if data.credentials is not None:
            provider.credentials = data.credentials
        if data.years_of_experience is not None:
            provider.years_of_experience = data.years_of_experience
        if data.accepting_new_patients is not None:
            provider.accepting_new_patients = data.accepting_new_patients
        if data.languages_spoken is not None:
            provider.languages_spoken = data.languages_spoken
        if data.accepted_insurances is not None:
            provider.accepted_insurances = data.accepted_insurances
        if data.certifications is not None:
            provider.certifications = data.certifications

        return await self.repository.update(provider)

    async def delete_provider(self, provider_id: UUID):
        provider = await self.get_provider_or_raise(provider_id)
        return await self.repository.soft_delete(provider)

    async def list_providers(self, skip: int = 0, limit: int = 100):
        return await self.repository.get_all(skip=skip, limit=limit)

    async def list_by_specialty(self, specialty: str):
        return await self.repository.get_by_specialty(specialty)

    async def list_accepting_patients(self):
        return await self.repository.get_accepting_patients()

    async def count_providers(self):
        return await self.repository.count()
