"""
Dashboard page - Overview of system metrics and patient statistics

This page will display:
- Active patients count
- Pending appointments
- Recent triage results
- System health metrics
"""

import streamlit as st

st.set_page_config(
    page_title="Dashboard - Patient Triage System",
    page_icon="🏠",
    layout="wide",
)

st.title("🏠 Dashboard")
st.markdown("---")

# Placeholder for Phase 1+
st.info("📊 Dashboard metrics will be available in Phase 1")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Patients", value="0", delta="0")

with col2:
    st.metric(label="Pending Appointments", value="0", delta="0")

with col3:
    st.metric(label="Today's Triage", value="0", delta="0")

with col4:
    st.metric(label="Critical Cases", value="0", delta="0")

st.markdown("---")
st.markdown("## Recent Activity")
st.info(
    "Recent activity will be displayed here once authentication and patient management are implemented"
)
