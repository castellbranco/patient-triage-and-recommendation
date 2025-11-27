"""
Appointment model - represents an appointment entity in the database.
"""
from datetime import datetime
import uuid

from typing import Optional
from sqlalchemy import (
    CheckConstraint,
    Index,
    DateTime,
    ForeignKey,
    String, 
    Integer,
    Text
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import (
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)


class Appointment(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """ Appointment model represents an schedule appointment"""
    
    __tablename__ = "appointments"

    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, doc="Reference to the patient")
    provider_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("providers.id", ondelete="RESTRICT"), nullable=False, doc="Reference to the provider")
    
    appointment_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False, doc="Date and Time of the appointment")
    duration: Mapped[int] = mapped_column(Integer, nullable=False, doc="Duration of the appointment in minutes")
    
    status: Mapped[str] = mapped_column(String(), default="scheduled", server_default="scheduled", nullable=False, doc="Status of the appointment (e.g., scheduled, confirmed, completed, canceled)")
    type: Mapped[Optional[str]] = mapped_column(String(), nullable=True, doc="Type of appointment (e.g., consultation, follow-up, emergency, telemedicine)")
     
    chief_complaint: Mapped[Optional[str]] = mapped_column(Text(), nullable=True, doc="Main reason for the appointment")
    symptoms: Mapped[dict] = mapped_column(JSONB, server_default = "[]", nullable=False, doc="List of symptoms (e.g., [{'icd10': 'R51', 'name': 'Headache', severity': 'mild'}] )")
    diagnosis: Mapped[dict] = mapped_column(JSONB, server_default = "[]", nullable=False, doc="Diagnosis codes (e.g., [{'icd10': 'J00', 'name': 'Acute nasopharyngitis (common cold)'}] )")
    notes: Mapped[Optional[str]] = mapped_column(Text(), nullable=True, doc="Additional notes for the appointment")
    
    canceled_by_and_why: Mapped[Optional[dict]] = mapped_column(JSONB, server_default = "{}" , nullable=True, doc="Details about who canceled the appointment and why (e.g., {'canceled_by': 'patient', 'reason': 'feeling better'})")

    patient: Mapped["Patient"] = relationship("Patient", back_populates="appointments", lazy="selectin", doc="Associated patient")
    provider: Mapped["Provider"] = relationship("Provider", back_populates="appointments", lazy="selectin", doc="Associated provider")

    __table_args__ = (
        CheckConstraint("status IN ('scheduled', 'confirmed', 'completed', 'cancelled', 'no_show')", name="chk_appointment_status_valid"),
        CheckConstraint("appointment_datetime >= now() - interval '1 year'", name="chk_appointment_datetime_recent"),
        Index("idx_appointment_patient_id", "patient_id"),
        Index("idx_appointment_provider_id", "provider_id"),
        Index("idx_appointment_scheduled_date", "provider_id", "appointment_datetime"),
        Index("idx_appointment_status", "status"),
        Index("idx_appointment_no_double_book", "provider_id", "appointment_datetime", unique=True),
        Index("idx_appointment_symptoms", "symptoms", postgresql_using="gin"),
        Index("idx_appointment_diagnosis", "diagnosis", postgresql_using="gin"),      
    )
    
    def __repr__(self) -> str:
        """String representation of the Appointment instance."""
        return f"<Appointment(id={self.id}, patient_id={self.patient_id}, provider_id={self.provider_id}, appointment_datetime={self.appointment_datetime}, status={self.status})>"