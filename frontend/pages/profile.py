"""
User Profile page - Manage user account and preferences

This page will allow users to:
- View and edit profile information
- Change password
- Manage notification preferences
- View activity history
"""

import streamlit as st

st.set_page_config(
    page_title="Profile - Patient Triage System",
    page_icon="👤",
    layout="wide",
)

st.title("👤 User Profile")
st.markdown("---")

# Placeholder for Phase 1+
st.info("🔐 User authentication and profiles will be available in Phase 1")

st.markdown("## Profile Information")
st.text_input("Full Name", value="", placeholder="Enter your full name")
st.text_input("Email", value="", placeholder="user@example.com")
st.selectbox("Role", ["Doctor", "Nurse", "Administrator"])

st.markdown("## Security")
st.button("Change Password", disabled=True)

st.markdown("## Preferences")
st.checkbox("Enable email notifications")
st.checkbox("Enable SMS alerts for critical cases")
