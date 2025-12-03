"""
User Service Module
"""

from typing import Optional, List
from uuid import UUID

import bcrypt

from infrastructure.database.models.user import User
from infrastructure.database.schemas.user import UserCreate, UserUpdate
from infrastructure.repo.user import UserRepository
from services.errors import EmailAlreadyExistsError, UserNotFoundError


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # Truncate to 72 bytes (bcrypt limit)
    password_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    password_bytes = plain_password.encode("utf-8")[:72]
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


class UserService:

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, data: UserCreate, role: str = "patient") -> User:
        if await self.repository.email_exists(data.email):
            raise EmailAlreadyExistsError(data.email)

        hashed = hash_password(data.password)

        user = User(
            email=data.email,
            hashed_password=hashed,
            first_name=data.first_name,
            last_name=data.last_name,
            phone_number=data.phone_number,
            role=role,
            is_active=True,
            is_verified=False,
        )

        return await self.repository.create(user)

    async def get_user(self, user_id: UUID) -> Optional[User]:
        return await self.repository.get_by_id(user_id)

    async def get_user_or_raise(self, user_id: UUID) -> User:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(str(user_id))
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        return await self.repository.get_by_email(email)

    async def update_user(self, user_id: UUID, data: UserUpdate) -> User:
        user = await self.get_user_or_raise(user_id)

        if data.email is not None and data.email != user.email:
            if await self.repository.email_exists(data.email):
                raise EmailAlreadyExistsError(data.email)
            user.email = data.email

        if data.first_name is not None:
            user.first_name = data.first_name

        if data.last_name is not None:
            user.last_name = data.last_name

        if data.phone_number is not None:
            user.phone_number = data.phone_number

        if data.password is not None:
            user.hashed_password = hash_password(data.password)

        return await self.repository.update(user)

    async def delete_user(self, user_id: UUID) -> User:
        user = await self.get_user_or_raise(user_id)
        return await self.repository.soft_delete(user)

    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return await self.repository.get_all(skip=skip, limit=limit)

    async def count_users(self) -> int:
        return await self.repository.count()

    async def get_users_by_role(self, role: str) -> List[User]:
        return await self.repository.get_by_role(role)

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        user = await self.repository.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user
