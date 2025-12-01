"""
Appointment Schema Module
"""

from uuid import UUID
from typing import Literal, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


AppointmentStatus = Literal["scheduled", "confirmed", "completed", "cancelled", "no_show"]
AppointmentType = Literal["consultation", "follow_up", "emergency", "telemedicine"]


class SymptomSchema(BaseModel):
    icd10: Optional[str] = Field(None, max_length=10)
    name: str = Field(..., min_length=1, max_length=200)
    severity: Optional[str] = Field(None, max_length=20)


class DiagnosisSchema(BaseModel):
    icd10: Optional[str] = Field(None, max_length=10)
    name: str = Field(..., min_length=1, max_length=200)


class CancellationSchema(BaseModel):
    canceled_by: str = Field(..., max_length=50)
    reason: Optional[str] = Field(None, max_length=500)


class AppointmentBase(BaseModel):
    appointment_datetime: datetime
    duration: int = Field(..., ge=5, le=480)
    type: Optional[AppointmentType] = None
    chief_complaint: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=2000)


class AppointmentCreate(AppointmentBase):
    patient_id: UUID
    provider_id: UUID
    symptoms: list[SymptomSchema] = Field(default_factory=list)


class AppointmentUpdate(BaseModel):
    appointment_datetime: Optional[datetime] = None
    duration: Optional[int] = Field(None, ge=5, le=480)
    status: Optional[AppointmentStatus] = None
    type: Optional[AppointmentType] = None
    chief_complaint: Optional[str] = Field(None, max_length=500)
    symptoms: Optional[list[SymptomSchema]] = None
    diagnosis: Optional[list[DiagnosisSchema]] = None
    notes: Optional[str] = Field(None, max_length=2000)
    canceled_by_and_why: Optional[CancellationSchema] = None


class AppointmentResponse(AppointmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    patient_id: UUID
    provider_id: UUID
    status: AppointmentStatus
    symptoms: list[SymptomSchema] = Field(default_factory=list)
    diagnosis: list[DiagnosisSchema] = Field(default_factory=list)
    canceled_by_and_why: Optional[CancellationSchema] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class AppointmentListResponse(BaseModel):
    appointments: list[AppointmentResponse]
    total: int
    page: int
    page_size: int
