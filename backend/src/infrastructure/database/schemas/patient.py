"""
Patient Schema Module
"""

from uuid import UUID
from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class AllergySchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    severity: Optional[str] = Field(None, max_length=20)


class ChronicConditionSchema(BaseModel):
    icd10: Optional[str] = Field(None, max_length=10)
    name: str = Field(..., min_length=1, max_length=200)


class MedicationSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    dosage: Optional[str] = Field(None, max_length=50)


class EmergencyContactSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    relationship: Optional[str] = Field(None, max_length=50)


class PatientBase(BaseModel):
    date_of_birth: date
    gender: Optional[str] = Field(None, max_length=20)
    blood_type: Optional[str] = Field(None, max_length=5)
    address_line1: Optional[str] = Field(None, max_length=200)
    address_line2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    insurance_provider: Optional[str] = Field(None, max_length=100)
    insurance_policy_number: Optional[str] = Field(None, max_length=50)


class PatientRegister(PatientBase):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    allergies: list[AllergySchema] = Field(default_factory=list)
    chronic_conditions: list[ChronicConditionSchema] = Field(default_factory=list)
    medications: list[MedicationSchema] = Field(default_factory=list)
    emergency_contact: Optional[EmergencyContactSchema] = None


class PatientCreate(PatientBase):
    user_id: UUID
    allergies: list[AllergySchema] = Field(default_factory=list)
    chronic_conditions: list[ChronicConditionSchema] = Field(default_factory=list)
    medications: list[MedicationSchema] = Field(default_factory=list)
    emergency_contact: Optional[EmergencyContactSchema] = None


class PatientUpdate(BaseModel):
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=20)
    blood_type: Optional[str] = Field(None, max_length=5)
    address_line1: Optional[str] = Field(None, max_length=200)
    address_line2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    insurance_provider: Optional[str] = Field(None, max_length=100)
    insurance_policy_number: Optional[str] = Field(None, max_length=50)
    allergies: Optional[list[AllergySchema]] = None
    chronic_conditions: Optional[list[ChronicConditionSchema]] = None
    medications: Optional[list[MedicationSchema]] = None
    emergency_contact: Optional[EmergencyContactSchema] = None


class PatientResponse(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    allergies: list[AllergySchema] = Field(default_factory=list)
    chronic_conditions: list[ChronicConditionSchema] = Field(default_factory=list)
    medications: list[MedicationSchema] = Field(default_factory=list)
    emergency_contact: Optional[EmergencyContactSchema] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class PatientListResponse(BaseModel):
    patients: list[PatientResponse]
    total: int
    page: int
    page_size: int
