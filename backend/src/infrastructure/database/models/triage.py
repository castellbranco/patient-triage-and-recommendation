"""
Triage models - TriageRule and TriageResult entities for the triage engine.
"""

import enum
import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Enum as SAEnum,
    Boolean,
    Float,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.base import (
    Base,
    TimestampMixin,
    UUIDMixin,
)

if TYPE_CHECKING:
    from infrastructure.database.models.patient import Patient
    from infrastructure.database.models.appointment import Appointment


class UrgencyLevel(str, enum.Enum):
    """Urgency levels for triage assessment."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EMERGENCY = "emergency"


class TriageRule(Base, UUIDMixin, TimestampMixin):
    """
    TriageRule maps ICD-10 code patterns to urgency levels and specialties.

    Used to determine the urgency of a patient's condition based on their
    symptoms (mapped to ICD-10 codes via NLM API).

    Example:
        icd10_pattern: "R07%" (chest pain codes)
        urgency_level: HIGH
        recommended_specialty: "Cardiology"
    """

    __tablename__ = "triage_rules"

    icd10_pattern: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        doc="ICD-10 code pattern (supports SQL LIKE wildcards, e.g., 'R07%')",
    )

    condition_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Human-readable name of the condition (e.g., 'Chest Pain')",
    )

    urgency_level: Mapped[UrgencyLevel] = mapped_column(
        SAEnum(UrgencyLevel, name="urgency_level_enum", create_type=True),
        nullable=False,
        index=True,
        doc="Urgency level: LOW, MEDIUM, HIGH, EMERGENCY",
    )

    recommended_specialty: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Recommended medical specialty (e.g., 'Cardiology', 'Neurology')",
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text(),
        nullable=True,
        doc="Additional description or notes about this rule",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
        doc="Whether this rule is currently active",
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
        doc="Priority for rule matching (higher = more priority)",
    )

    # Indexes and constraints for efficient querying
    __table_args__ = (
        CheckConstraint("char_length(icd10_pattern) >= 1", name="chk_rule_pattern_not_empty"),
        CheckConstraint("char_length(condition_name) >= 1", name="chk_rule_condition_not_empty"),
        CheckConstraint("char_length(recommended_specialty) >= 1", name="chk_rule_specialty_not_empty"),
        CheckConstraint("priority >= 0", name="chk_rule_priority_non_negative"),
        Index("ix_triage_rules_pattern_active", "icd10_pattern", "is_active"),
        Index("ix_triage_rules_urgency_active", "urgency_level", "is_active"),
    )

    def __repr__(self) -> str:
        return (
            f"<TriageRule(pattern='{self.icd10_pattern}', "
            f"urgency={self.urgency_level.value}, "
            f"specialty='{self.recommended_specialty}')>"
        )


class TriageResult(Base, UUIDMixin, TimestampMixin):
    """
    TriageResult stores the outcome of a patient's triage assessment.

    Each time a patient goes through the triage process, a record is created
    with their symptoms, the calculated urgency, and specialty recommendation.
    """

    __tablename__ = "triage_results"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Reference to the patient being triaged",
    )

    # Input: Raw symptoms from the patient
    raw_symptoms: Mapped[str] = mapped_column(
        Text(),
        nullable=False,
        doc="Original symptom text provided by the patient",
    )

    # Processed: Standardized symptoms with ICD-10 codes
    processed_symptoms: Mapped[list] = mapped_column(
        JSONB,
        server_default="[]",
        nullable=False,
        doc="Processed symptoms with ICD-10 codes: [{'code': 'R07.9', 'name': 'Chest pain', 'consumer_name': '...'}]",
    )

    # Matched rules that led to the decision
    matched_rules: Mapped[list] = mapped_column(
        JSONB,
        server_default="[]",
        nullable=False,
        doc="Rules that matched: [{'rule_id': '...', 'pattern': 'R07%', 'urgency': 'high'}]",
    )

    # Final decision
    urgency_level: Mapped[UrgencyLevel] = mapped_column(
        SAEnum(UrgencyLevel, name="urgency_level_enum", create_type=False),
        nullable=False,
        index=True,
        doc="Final calculated urgency level",
    )

    recommended_specialty: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Recommended specialty based on highest urgency rule",
    )

    # Optional: Link to appointment if one was created
    appointment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("appointments.id", ondelete="SET NULL"),
        nullable=True,
        doc="Reference to appointment created from this triage (if any)",
    )

    # Additional metadata
    triage_notes: Mapped[Optional[str]] = mapped_column(
        Text(),
        nullable=True,
        doc="Additional notes from the triage process",
    )

    ai_confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        doc="AI confidence score for the triage decision (0.0 to 1.0)",
    )

    # Relationships
    patient: Mapped["Patient"] = relationship(
        "Patient",
        back_populates="triage_results",
        lazy="selectin",
    )

    appointment: Mapped[Optional["Appointment"]] = relationship(
        "Appointment",
        lazy="selectin",
    )

    # Indexes and constraints
    __table_args__ = (
        CheckConstraint("char_length(raw_symptoms) >= 1", name="chk_result_symptoms_not_empty"),
        CheckConstraint("char_length(recommended_specialty) >= 1", name="chk_result_specialty_not_empty"),
        CheckConstraint(
            "ai_confidence IS NULL OR (ai_confidence >= 0.0 AND ai_confidence <= 1.0)",
            name="chk_result_confidence_range",
        ),
        Index("ix_triage_results_patient_created", "patient_id", "created_at"),
        Index("ix_triage_results_urgency_created", "urgency_level", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<TriageResult(patient_id={self.patient_id}, "
            f"urgency={self.urgency_level.value}, "
            f"specialty='{self.recommended_specialty}')>"
        )
