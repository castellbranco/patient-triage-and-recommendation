"""
API Client for communicating with the FastAPI backend.

Handles:
- HTTP requests to backend endpoints
- Authentication token management
- Error handling and retries
- Response parsing
"""

import os
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

# Load environment from root .env
load_dotenv()


class APIClient:
    """Client for interacting with the Patient Triage Backend API"""

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize API client.

        Args:
            base_url: Backend API URL. If None, reads from BACKEND_API_URL env var
        """
        self.base_url = base_url or os.getenv("BACKEND_API_URL", "http://localhost:8000")
        self.token: Optional[str] = None
        self.session = requests.Session()

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def health_check(self) -> Dict[str, Any]:
        """
        Check backend health status.

        Returns:
            Health check response from backend

        Raises:
            requests.RequestException: If request fails
        """
        url = f"{self.base_url}/api/public/v1/health"
        response = self.session.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and obtain JWT token.

        Args:
            email: User email
            password: User password

        Returns:
            Authentication response with token

        Note:
            Will be implemented in Phase 1
        """
        raise NotImplementedError("Authentication will be implemented in Phase 1")

    def set_token(self, token: str) -> None:
        """
        Set authentication token for subsequent requests.

        Args:
            token: JWT authentication token
        """
        self.token = token

    def clear_token(self) -> None:
        """Clear authentication token (logout)"""
        self.token = None


# Singleton instance
api_client = APIClient()
