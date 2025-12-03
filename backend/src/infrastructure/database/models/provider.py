"""
Provider Model - Represents a healthcare provider profile linked to a user.
"""

import uuid

from typing import Optional
from sqlalchemy import String, ForeignKey, CheckConstraint, Index, UniqueConstraint, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from infrastructure.database.base import (
    Base,
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
)


class Provider(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "providers"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        doc="Reference to the User Table",
    )

    specialty: Mapped[str] = mapped_column(
        String(), nullable=False, doc="Medical specialty of the provider"
    )
    license_number: Mapped[str] = mapped_column(
        String(), nullable=False, unique=True, doc="Unique medical license number"
    )
    credentials: Mapped[Optional[str]] = mapped_column(
        String(), nullable=True, doc="Professional credentials (e.g., MD, DO)"
    )

    languages_spoken: Mapped[dict] = mapped_column(
        JSONB,
        server_default='["English"]',
        nullable=False,
        doc="Languages spoken (e.g., ['English', 'Spanish'])",
    )
    accepted_insurances: Mapped[dict] = mapped_column(
        JSONB,
        server_default="[]",
        nullable=False,
        doc="List of accepted insurance (e.g., ['Aetna', 'Blue Cross'])",
    )
    certifications: Mapped[dict] = mapped_column(
        JSONB,
        server_default="[]",
        nullable=False,
        doc="List of certifications (e.g., ['Board Certified in Internal Medicine'])",
    )

    accepting_new_patients: Mapped[bool] = mapped_column(
        Boolean(),
        nullable=False,
        server_default="true",
        doc="Indicates if the provider is accepting new patients",
    )
    years_of_experience: Mapped[Optional[int]] = mapped_column(
        nullable=True, doc="Number of years of experience"
    )
    additional_info: Mapped[Optional[dict]] = mapped_column(
        JSONB, server_default="[]", nullable=True, doc="Additional information about the provider"
    )

    user: Mapped["User"] = relationship(
        "User", back_populates="provider", lazy="selectin", doc="Association to the User account"
    )
    appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment",
        back_populates="provider",
        lazy="selectin",
        doc="List of appointments for the provider",
    )

    __table_args__ = (
        Index("idx_providers_user_id", "user_id"),
        Index("idx_providers_specialty", "specialty"),
        Index("idx_providers_accepting_new_patients", "accepting_new_patients"),
        Index("idx_providers_languages_spoken", "languages_spoken", postgresql_using="gin"),
        Index("idx_providers_accepted_insurances", "accepted_insurances", postgresql_using="gin"),
    )

    def __repr__(self) -> str:
        """String representation of the Provider model."""
        return f"<Provider(id={self.id}, user_id={self.user_id}, specialty={self.specialty}, license_number={self.license_number})>"
