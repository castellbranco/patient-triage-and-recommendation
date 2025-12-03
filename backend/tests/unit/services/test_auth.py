"""
Auth Service Tests - Unit tests for AuthService business logic
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from services.auth import AuthService
from services.errors import InvalidCredentialsError, UserNotActiveError


@pytest.fixture
def mock_user_service():
    """Mock UserService for testing."""
    return AsyncMock()


@pytest.fixture
def auth_service(mock_user_service):
    """Create AuthService with mocked dependencies."""
    return AuthService(mock_user_service)


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    user = MagicMock()
    user.id = uuid4()
    user.email = "test@example.com"
    user.role = "patient"
    user.is_active = True
    # bcrypt hash for "password123"
    user.hashed_password = "$2b$12$m2JEAfxpmsF0.TCKjndhM.ffQSO2f4SgQryDYFPvyLePMSzMiJqmm"
    return user


class TestAuthServiceLogin:
    """Tests for AuthService.login()"""

    async def test_login_success(self, auth_service, mock_user_service, mock_user):
        """Valid credentials should return tokens."""
        mock_user_service.get_user_by_email.return_value = mock_user
        
        access_token, refresh_token = await auth_service.login(
            email="test@example.com",
            password="password123",
        )
        
        assert access_token is not None
        assert refresh_token is not None
        assert isinstance(access_token, str)
        assert isinstance(refresh_token, str)
        mock_user_service.get_user_by_email.assert_called_once_with("test@example.com")

    async def test_login_user_not_found(self, auth_service, mock_user_service):
        """Non-existent user should raise InvalidCredentialsError."""
        mock_user_service.get_user_by_email.return_value = None
        
        with pytest.raises(InvalidCredentialsError):
            await auth_service.login(
                email="nonexistent@example.com",
                password="password123",
            )

    async def test_login_wrong_password(self, auth_service, mock_user_service, mock_user):
        """Wrong password should raise InvalidCredentialsError."""
        mock_user_service.get_user_by_email.return_value = mock_user
        
        with pytest.raises(InvalidCredentialsError):
            await auth_service.login(
                email="test@example.com",
                password="wrongpassword",
            )

    async def test_login_inactive_user(self, auth_service, mock_user_service, mock_user):
        """Inactive user should raise UserNotActiveError."""
        mock_user.is_active = False
        mock_user_service.get_user_by_email.return_value = mock_user
        
        with pytest.raises(UserNotActiveError):
            await auth_service.login(
                email="test@example.com",
                password="password123",
            )


class TestAuthServiceRefresh:
    """Tests for AuthService.refresh_tokens()"""

    def test_refresh_tokens_returns_new_tokens(self, auth_service):
        """Refresh should return new access and refresh tokens."""
        subject = {
            "user_id": str(uuid4()),
            "email": "test@example.com",
            "role": "patient",
        }
        
        access_token, refresh_token = auth_service.refresh_tokens(subject)
        
        assert access_token is not None
        assert refresh_token is not None
        assert isinstance(access_token, str)
        assert isinstance(refresh_token, str)


class TestAuthServiceGetUser:
    """Tests for AuthService.get_user_from_token()"""

    async def test_get_user_from_token_success(self, auth_service, mock_user_service, mock_user):
        """Valid user_id should return user."""
        mock_user_service.get_user_or_raise.return_value = mock_user
        user_id = str(mock_user.id)
        
        result = await auth_service.get_user_from_token(user_id)
        
        assert result == mock_user
        mock_user_service.get_user_or_raise.assert_called_once()
