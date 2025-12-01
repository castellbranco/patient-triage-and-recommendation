"""
User API Module - Routes for user endpoints

User creation is handled via domain-specific registration:
- Patients: POST /patients/register
- Providers: POST /providers/register
- Admins: Seeded or internal process

This API provides read/update/delete for existing users.
"""

from uuid import UUID

from fastapi import APIRouter, Query

from infrastructure.api.utils import (
    Pagination,
    UserServiceDep,
    conflict_exception,
    not_found_exception,
)
from infrastructure.database.schemas.user import (
    UserListResponse,
    UserResponse,
    UserRole,
    UserUpdate,
)
from services.errors import EmailAlreadyExistsError, UserNotFoundError


router = APIRouter(prefix="/users", tags=["Users"])


# =============================================================================
# Collection Endpoints: /users
# =============================================================================


@router.get(
    "",
    response_model=UserListResponse,
    summary="List users",
    responses={200: {"description": "Users retrieved"}},
)
async def list_users(
    service: UserServiceDep,
    pagination: Pagination,
    role: UserRole | None = Query(None, description="Filter by role"),
) -> UserListResponse:
    """List all users with pagination and optional role filter."""
    if role:
        users = await service.get_users_by_role(role)
        total = len(users)
        users = users[pagination.skip : pagination.skip + pagination.limit]
    else:
        users = await service.list_users(skip=pagination.skip, limit=pagination.limit)
        total = await service.count_users()

    return UserListResponse(
        users=[UserResponse.model_validate(user) for user in users],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


# =============================================================================
# Resource Endpoints: /users/{user_id}
# =============================================================================


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user",
    responses={
        200: {"description": "User retrieved"},
        404: {"description": "User not found"},
    },
)
async def get_user(user_id: UUID, service: UserServiceDep) -> UserResponse:
    """Get a user by ID."""
    try:
        user = await service.get_user_or_raise(user_id)
        return UserResponse.model_validate(user)
    except UserNotFoundError:
        raise not_found_exception("User", str(user_id))


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    responses={
        200: {"description": "User updated"},
        404: {"description": "User not found"},
        409: {"description": "Email already registered"},
    },
)
async def update_user(
    user_id: UUID, data: UserUpdate, service: UserServiceDep
) -> UserResponse:
    """Update a user's profile. Only provided fields are updated."""
    try:
        user = await service.update_user(user_id, data)
        return UserResponse.model_validate(user)
    except UserNotFoundError:
        raise not_found_exception("User", str(user_id))
    except EmailAlreadyExistsError:
        raise conflict_exception("Email", data.email)


@router.delete(
    "/{user_id}",
    response_model=UserResponse,
    summary="Delete user",
    responses={
        200: {"description": "User deleted"},
        404: {"description": "User not found"},
    },
)
async def delete_user(user_id: UUID, service: UserServiceDep) -> UserResponse:
    """Soft-delete a user (data retained for audit)."""
    try:
        user = await service.delete_user(user_id)
        return UserResponse.model_validate(user)
    except UserNotFoundError:
        raise not_found_exception("User", str(user_id))
