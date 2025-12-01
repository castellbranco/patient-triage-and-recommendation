"""
User Schema Module for Database Interaction - DRY Principle
"""
from uuid import UUID
from typing import Literal, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict



UserRole = Literal["admin", "provider", "patient"]

class UserBase(BaseModel):
    """
    Base schema with fields shared across Create and Response.
    """
    
    email: EmailStr = Field(..., description="User's email address (must be unique)")
    first_name: str = Field(..., min_length=1, max_length=100, description="User's first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="User's last name")
    phone_number: Optional[str] = Field(None, max_length=20, description="User's phone number (optional)")


class UserCreate(UserBase):
    """
    Schema for user registration (POST /users).
    """
    password: str = Field(..., min_length=8, max_length=128, description="Plain text password (will be hashed server-side)")


class UserUpdate(BaseModel):
    """
    Schema for updating user profile (PATCH /users/{id}).
    """

    email: Optional[EmailStr] = Field(None, description="New email address")
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="New first name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="New last name")
    phone_number: Optional[str] = Field(None, max_length=20, description="New phone number")
    password: Optional[str] = Field(None, min_length=8, max_length=128, description="New password (will be hashed server-side)")

class UserResponse(UserBase):
    """
    Schema for user data returned to clients (GET /users/{id}).
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(..., description="Unique identifier for the user")
    role: UserRole = Field(..., description="User's role: admin, provider, or patient")
    is_active: bool = Field(..., description="Whether the account is active (false = deactivated)")
    is_verified: bool = Field(..., description="Whether the email has been verified")
    created_at: datetime = Field(..., description="Timestamp when the user was created")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the user was last updated")
    last_login_at: Optional[datetime] = Field(None, description="Timestamp of the user's last login")

class UserListResponse(BaseModel):
    """
    Schema for paginated list of users (GET /users).
    """
    
    users: list[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users matching the query")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of users per page")
