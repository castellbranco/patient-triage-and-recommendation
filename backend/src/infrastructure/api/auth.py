"""
Auth API Module - Routes for authentication endpoints
"""

from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Security

from fastapi_jwt import JwtAuthorizationCredentials

from infrastructure.api.utils import AuthServiceDep
from infrastructure.database.schemas.auth import (
    LoginRequest,
    TokenResponse,
)
from infrastructure.database.schemas.user import UserResponse
from services.auth import access_security, refresh_security


router = APIRouter(prefix="/auth", tags=["Authentication"], route_class=DishkaRoute)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials or inactive account"},
    },
)
async def login(data: LoginRequest, service: AuthServiceDep) -> TokenResponse:
    """
    Authenticate with email and password.
    
    Returns access and refresh JWT tokens.
    """
    access_token, refresh_token = await service.login(data.email, data.password)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh tokens",
    responses={
        200: {"description": "Tokens refreshed"},
        401: {"description": "Invalid or expired refresh token"},
    },
)
async def refresh_tokens(
    service: AuthServiceDep,
    credentials: JwtAuthorizationCredentials = Security(refresh_security),
) -> TokenResponse:
    """
    Get new access/refresh tokens using a valid refresh token.
    """
    access_token, refresh_token = service.refresh_tokens(credentials.subject)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    responses={
        200: {"description": "Current user info"},
        401: {"description": "Invalid or expired access token"},
    },
)
async def get_current_user(
    service: AuthServiceDep,
    credentials: JwtAuthorizationCredentials = Security(access_security),
) -> UserResponse:
    """
    Get the currently authenticated user's information.
    """
    user = await service.get_user_from_token(credentials["user_id"])
    return UserResponse.model_validate(user)
