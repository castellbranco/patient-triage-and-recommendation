"""
Provider Schema Module
"""

from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ProviderBase(BaseModel):
    specialty: str = Field(..., min_length=1, max_length=100)
    license_number: str = Field(..., min_length=1, max_length=50)
    credentials: Optional[str] = Field(None, max_length=20)
    accepting_new_patients: bool = True
    years_of_experience: Optional[int] = Field(None, ge=0)


class ProviderCreate(ProviderBase):
    user_id: UUID
    languages_spoken: list[str] = Field(default_factory=lambda: ["English"])
    accepted_insurances: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    additional_info: Optional[dict] = None


class ProviderUpdate(BaseModel):
    specialty: Optional[str] = Field(None, min_length=1, max_length=100)
    license_number: Optional[str] = Field(None, min_length=1, max_length=50)
    credentials: Optional[str] = Field(None, max_length=20)
    languages_spoken: Optional[list[str]] = None
    accepted_insurances: Optional[list[str]] = None
    certifications: Optional[list[str]] = None
    accepting_new_patients: Optional[bool] = None
    years_of_experience: Optional[int] = Field(None, ge=0)
    additional_info: Optional[dict] = None


class ProviderResponse(ProviderBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    languages_spoken: list[str] = Field(default_factory=lambda: ["English"])
    accepted_insurances: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    additional_info: Optional[dict] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ProviderListResponse(BaseModel):
    providers: list[ProviderResponse]
    total: int
    page: int
    page_size: int
