"""
Patient Service Module
"""

from uuid import UUID

from infrastructure.database.models.patient import Patient
from infrastructure.database.schemas.patient import PatientCreate, PatientRegister, PatientUpdate
from infrastructure.database.schemas.user import UserCreate
from infrastructure.repo.patient import PatientRepository
from services.user import UserService
from services.errors import PatientNotFoundError, PatientAlreadyExistsError


class PatientService:

    def __init__(self, repository: PatientRepository, user_service: UserService):
        self.repository = repository
        self.user_service = user_service

    async def register_patient(self, data: PatientRegister):
        user_data = UserCreate(
            email=data.email,
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name,
            phone_number=data.phone_number,
        )
        user = await self.user_service.create_user(user_data, role="patient")

        patient = Patient(
            user_id=user.id,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            blood_type=data.blood_type,
            address_line1=data.address_line1,
            address_line2=data.address_line2,
            city=data.city,
            postal_code=data.postal_code,
            country=data.country,
            insurance_provider=data.insurance_provider,
            insurance_policy_number=data.insurance_policy_number,
            allergies=[a.model_dump() for a in data.allergies],
            chronic_conditions=[c.model_dump() for c in data.chronic_conditions],
            medications=[m.model_dump() for m in data.medications],
            emergency_contact=data.emergency_contact.model_dump() if data.emergency_contact else {},
        )

        return await self.repository.create(patient)

    async def create_patient(self, data: PatientCreate):
        if await self.repository.user_has_patient(data.user_id):
            raise PatientAlreadyExistsError(str(data.user_id))

        patient = Patient(
            user_id=data.user_id,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            blood_type=data.blood_type,
            address_line1=data.address_line1,
            address_line2=data.address_line2,
            city=data.city,
            postal_code=data.postal_code,
            country=data.country,
            insurance_provider=data.insurance_provider,
            insurance_policy_number=data.insurance_policy_number,
            allergies=[a.model_dump() for a in data.allergies],
            chronic_conditions=[c.model_dump() for c in data.chronic_conditions],
            medications=[m.model_dump() for m in data.medications],
            emergency_contact=data.emergency_contact.model_dump() if data.emergency_contact else {},
        )

        return await self.repository.create(patient)

    async def get_patient(self, patient_id: UUID):
        return await self.repository.get_by_id(patient_id)

    async def get_patient_or_raise(self, patient_id: UUID):
        patient = await self.repository.get_by_id(patient_id)
        if not patient:
            raise PatientNotFoundError(str(patient_id))
        return patient

    async def get_patient_by_user_id(self, user_id: UUID):
        return await self.repository.get_by_user_id(user_id)

    async def update_patient(self, patient_id: UUID, data: PatientUpdate):
        patient = await self.get_patient_or_raise(patient_id)

        if data.date_of_birth is not None:
            patient.date_of_birth = data.date_of_birth
        if data.gender is not None:
            patient.gender = data.gender
        if data.blood_type is not None:
            patient.blood_type = data.blood_type
        if data.address_line1 is not None:
            patient.address_line1 = data.address_line1
        if data.address_line2 is not None:
            patient.address_line2 = data.address_line2
        if data.city is not None:
            patient.city = data.city
        if data.postal_code is not None:
            patient.postal_code = data.postal_code
        if data.country is not None:
            patient.country = data.country
        if data.insurance_provider is not None:
            patient.insurance_provider = data.insurance_provider
        if data.insurance_policy_number is not None:
            patient.insurance_policy_number = data.insurance_policy_number
        if data.allergies is not None:
            patient.allergies = [a.model_dump() for a in data.allergies]
        if data.chronic_conditions is not None:
            patient.chronic_conditions = [c.model_dump() for c in data.chronic_conditions]
        if data.medications is not None:
            patient.medications = [m.model_dump() for m in data.medications]
        if data.emergency_contact is not None:
            patient.emergency_contact = data.emergency_contact.model_dump()

        return await self.repository.update(patient)

    async def delete_patient(self, patient_id: UUID):
        patient = await self.get_patient_or_raise(patient_id)
        return await self.repository.soft_delete(patient)

    async def list_patients(self, skip: int = 0, limit: int = 100):
        return await self.repository.get_all(skip=skip, limit=limit)

    async def count_patients(self):
        return await self.repository.count()

