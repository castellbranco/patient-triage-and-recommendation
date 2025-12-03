"""
Auth Service Module - JWT token management using fastapi-jwt
"""

import os
from datetime import timedelta
from uuid import UUID

from fastapi_jwt import JwtAccessBearer, JwtRefreshBearer

from infrastructure.database.models.user import User
from services.errors import InvalidCredentialsError, UserNotActiveError
from services.user import UserService, verify_password


# JWT Configuration from environment
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
JWT_ACCESS_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_EXPIRE_MINUTES", "30"))
JWT_REFRESH_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "7"))


# Initialize JWT security instances
access_security = JwtAccessBearer(
    secret_key=JWT_SECRET_KEY,
    auto_error=True,
    access_expires_delta=timedelta(minutes=JWT_ACCESS_EXPIRE_MINUTES),
)

refresh_security = JwtRefreshBearer(
    secret_key=JWT_SECRET_KEY,
    auto_error=True,
    refresh_expires_delta=timedelta(days=JWT_REFRESH_EXPIRE_DAYS),
)


class AuthService:
    """Service for authentication operations."""

    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def login(self, email: str, password: str) -> tuple[str, str]:
        """
        Authenticate user and return access/refresh tokens.
        """

        user = await self.user_service.get_user_by_email(email)

        if not user:
            raise InvalidCredentialsError()

        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise UserNotActiveError(user.email)

        # Create token subject with user info
        subject = {
            "user_id": str(user.id),
            "email": user.email,
            "role": user.role,
        }

        access_token = access_security.create_access_token(subject=subject)
        refresh_token = refresh_security.create_refresh_token(subject=subject)

        return access_token, refresh_token

    def refresh_tokens(self, subject: dict) -> tuple[str, str]:
        """
        Create new access/refresh tokens from existing subject.
        """

        access_token = access_security.create_access_token(subject=subject)
        refresh_token = refresh_security.create_refresh_token(subject=subject)

        return access_token, refresh_token

    async def get_user_from_token(self, user_id: str) -> User:
        """
        Get user from token subject.
        """

        return await self.user_service.get_user_or_raise(UUID(user_id))
