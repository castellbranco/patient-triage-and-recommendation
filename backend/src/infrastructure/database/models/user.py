"""
User Model - Represents a user in the system.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, CheckConstraint, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.base import (
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
    )

class User(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """User model representing a user in the system."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(), unique=True, nullable=False, doc="User's email address")
    hashed_password: Mapped[str] = mapped_column(String(), nullable=False, doc="Bcrypt hashed password")
    first_name: Mapped[str] = mapped_column(String(), nullable=False, doc= "User's first name")
    last_name: Mapped[str] = mapped_column(String(), nullable=False, doc="User's last name")  
    phone_number: Mapped[Optional[str]] = mapped_column(String(), nullable=True, doc="User's phone number(Optional)")
    
    role: Mapped[str] = mapped_column(String(), nullable=False, doc="User's role: admin, provider or patient")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False, doc="Account enabled (false = desactivated)")
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False, doc="Email verified status")
    last_login_at: Mapped[Optional[datetime]] = mapped_column(nullable=True, doc="Timestamp of the last login")
    
    patient: Mapped[Optional["Patient"]] = relationship("Patient", back_populates="user", uselist=False, lazy="selectin", doc = "Patient profile (if role='patient')")
    provider: Mapped[Optional["Provider"]] = relationship("Provider", back_populates="user", uselist=False, lazy="selectin", doc = "Provider profile (if role='provider')") 
    
    __table_args__ = (
        CheckConstraint("role IN ('admin', 'provider', 'patient')", name="chk_user_role_valid"),
        Index("idx_users_email", "email", unique=True, postgresql_where= (text("deleted_at IS NULL"))),
        Index("idx_users_role", "role"),
        Index("idx_users_is_verified", "is_verified"),
    )
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<User id={self.id} email={self.email} role={self.role} is_active={self.is_active}>"