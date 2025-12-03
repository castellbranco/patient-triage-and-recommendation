"""
Authentication utilities for Streamlit frontend.

Handles:
- Login/logout flow
- Session state management
- Token persistence
- Protected page routing
"""

from typing import Optional

import streamlit as st

from shared.api_client import api_client


def is_authenticated() -> bool:
    """
    Check if user is authenticated.

    Returns:
        True if user has valid session, False otherwise
    """
    return st.session_state.get("authenticated", False)


def get_current_user() -> Optional[dict]:
    """
    Get current authenticated user information.

    Returns:
        User data dict if authenticated, None otherwise
    """
    if is_authenticated():
        return st.session_state.get("user")
    return None


def login(email: str, password: str) -> bool:
    """
    Authenticate user with backend.

    Args:
        email: User email
        password: User password

    Returns:
        True if login successful, False otherwise

    Note:
        Will be implemented in Phase 1
    """
    # Placeholder - will be implemented in Phase 1
    # try:
    #     response = api_client.login(email, password)
    #     st.session_state.authenticated = True
    #     st.session_state.user = response["user"]
    #     st.session_state.token = response["access_token"]
    #     api_client.set_token(response["access_token"])
    #     return True
    # except Exception as e:
    #     st.error(f"Login failed: {str(e)}")
    #     return False
    return False


def logout() -> None:
    """
    Logout current user and clear session.
    """
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.token = None
    api_client.clear_token()


def require_auth():
    """
    Decorator/helper to require authentication for a page.

    Shows login form if user is not authenticated.

    Note:
        Will be implemented in Phase 1
    """
    if not is_authenticated():
        st.warning("⚠️ Authentication required. Please login.")
        st.info("Authentication will be implemented in Phase 1")
        st.stop()
