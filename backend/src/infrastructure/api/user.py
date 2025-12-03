"""
User API Module - Routes for user endpoints
"""

from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query

from infrastructure.api.utils import Pagination, UserServiceDep
from infrastructure.database.schemas.user import (
    AdminUserCreate,
    UserListResponse,
    UserResponse,
    UserRole,
    UserUpdate,
)


router = APIRouter(prefix="/users", tags=["Users"], route_class=DishkaRoute)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    summary="Register admin user",
    responses={
        201: {"description": "Admin user created"},
        409: {"description": "Email already registered"},
    },
)
async def register_admin(
    data: AdminUserCreate, service: UserServiceDep
) -> UserResponse:
    """Register a new admin user. In production, this should be protected."""
    user = await service.create_user(data, role=data.role)
    return UserResponse.model_validate(user)


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
    user = await service.get_user_or_raise(user_id)
    return UserResponse.model_validate(user)


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
    user = await service.update_user(user_id, data)
    return UserResponse.model_validate(user)


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
    user = await service.delete_user(user_id)
    return UserResponse.model_validate(user)
