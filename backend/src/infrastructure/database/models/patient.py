"""
Patient Model - Represents a patient profile linked to a user.
"""

import uuid

from datetime import date
from typing import Optional

from sqlalchemy import String, ForeignKey, CheckConstraint, Date, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.base import (
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
    )

class Patient(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """Patient model representing a patient profile linked to a user."""

    __tablename__ = "patients"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, doc="Reference to User table")
    
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False, doc="Patient's date of birth")
    gender: Mapped[Optional[str]] = mapped_column(String(), nullable=True, doc="Patient gender")
    blood_type: Mapped[Optional[str]] = mapped_column(String(), nullable=True, doc="Patient blood type")
    
    address_line1: Mapped[Optional[str]] = mapped_column(String(), nullable=True, doc="Patient address line 1")
    address_line2: Mapped[Optional[str]] = mapped_column(String(), nullable=True, doc="Patient address line 2 (Optional)")
    city: Mapped[Optional[str]] = mapped_column(String(), nullable=True, doc="Patient city")
    postal_code: Mapped[Optional[str]] = mapped_column(String(), nullable=True, doc="Patient postal code (Optional)")
    country: Mapped[Optional[str]] = mapped_column(String(), nullable=True, doc="Patient country (Optional)")
    
    allergies: Mapped[dict] = mapped_column(JSONB, server_default="[]", nullable=False, doc="List of allergies (e.g., [{'name': 'penicillin', 'severity': 'high'}])")
    chronic_conditions: Mapped[dict] = mapped_column(JSONB, server_default="[]", nullable=False, doc="List of chronic conditions (e.g., [{'icd10': 'E11', 'name': 'Type 2 diabetes'}])")
    medications: Mapped[dict] = mapped_column(JSONB, server_default="[]", nullable=False, doc="Current medications (e.g., [{'name': 'metformin', 'dosage': '500mg'}])")
    emergency_contact: Mapped[dict] = mapped_column(JSONB, server_default="{}", nullable=False, doc="Emergency contact info (e.g., {'name': 'John Doe', 'phone': '+1234567890'})")  
    
    insurance_provider: Mapped[Optional[str]] = mapped_column(String(), nullable=True, doc="Health insurance provider (Optional)") 
    insurance_policy_number: Mapped[Optional[str]] = mapped_column(String(), nullable=True, doc="Health insurance policy number (Optional)")
    
    user: Mapped["User"] = relationship("User", back_populates="patient", lazy="selectin", doc="Associated user account")
    appointments: Mapped[list["Appointment"]] = relationship("Appointment", back_populates="patient", lazy="selectin", doc="Patient's appointments")
    
    
    __table_args__ = (
        CheckConstraint("date_of_birth <= CURRENT_DATE", name="chk_patient_dob_valid"),
        Index("idx_patients_user_id", "user_id"),
        Index("idx_patients_allergies", "allergies", postgresql_using="gin"),
        Index("idx_patients_chronic_conditions", "chronic_conditions", postgresql_using="gin"),
        Index("idx_patients_medications", "medications", postgresql_using="gin"),
        Index("idx_patients_dob", "date_of_birth"),
    )
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Patient id={self.id} user_id={self.user_id} date_of_birth={self.date_of_birth}>"