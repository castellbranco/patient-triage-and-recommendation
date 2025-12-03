"""
Patient Triage & Management System - Streamlit Frontend

Main entry point for the Streamlit application.
"""

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Load environment variables from root .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Page configuration
st.set_page_config(
    page_title="Patient Triage System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .welcome-text {
        font-size: 1.2rem;
        text-align: center;
        color: #555;
        margin-bottom: 2rem;
    }
    .feature-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Main page
st.markdown(
    '<h1 class="main-header">🏥 Patient Triage & Management System</h1>', unsafe_allow_html=True
)
st.markdown(
    '<p class="welcome-text">Welcome to the automated patient triage system</p>',
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.image(
        "https://via.placeholder.com/200x100.png?text=Healthcare+Logo", use_container_width=True
    )
    st.markdown("---")
    st.markdown("### Navigation")
    st.info("Use the pages menu to navigate through the application")

    # System status
    st.markdown("---")
    st.markdown("### System Status")
    backend_url = os.getenv("BACKEND_API_URL", "http://localhost:8000")
    st.success(f"🟢 Backend: {backend_url}")
    st.info("ℹ️ Version: 0.1.0-mvp")

# Main content
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="feature-box">', unsafe_allow_html=True)
    st.markdown("### 📋 Patient Registration")
    st.markdown("Register new patients and manage patient information")
    st.markdown("**Status**: Coming in Phase 1")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="feature-box">', unsafe_allow_html=True)
    st.markdown("### 🩺 Symptom Triage")
    st.markdown("Automated triage based on patient symptoms and vital signs")
    st.markdown("**Status**: Coming in Phase 2")
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown('<div class="feature-box">', unsafe_allow_html=True)
    st.markdown("### 📅 Appointments")
    st.markdown("Schedule and manage patient appointments")
    st.markdown("**Status**: Coming in Phase 3")
    st.markdown("</div>", unsafe_allow_html=True)

# Information section
st.markdown("---")
st.markdown("## 🚀 About This System")

st.markdown(
    """
This Patient Triage & Management System demonstrates:

- **Symptom Standardization**: Integration with NLM Medical Conditions API for ICD-10 code validation
- **Automated Triage**: AI-powered triage recommendations based on symptoms and vital signs
- **Clean Architecture**: Backend built with FastAPI following clean architecture principles
- **Production-Ready**: Docker deployment, CI/CD, comprehensive testing

### 📖 Development Phases

The system is being built progressively through tagged releases:

1. **v0.1.0-mvp** (Current): Foundation with authentication and database
2. **v0.2.0-triage-core**: NLM API integration and triage engine
3. **v0.3.0-security**: RBAC and audit logging
4. **v0.4.0-clinical**: Medical records and prescriptions
5. **v0.5.0-scale**: Performance optimization with Redis
6. **v0.6.0-production**: Full observability and monitoring

### 🛠️ Technology Stack

**Backend**: FastAPI • PostgreSQL • SQLAlchemy • Alembic • Dishka
**Frontend**: Streamlit (current) • React + TypeScript (planned)
**Infrastructure**: Docker • GitHub Actions • Terraform • GCP/AWS
"""
)

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #888;">Built with FastAPI, Streamlit, and Clean Architecture principles</p>',
    unsafe_allow_html=True,
)
