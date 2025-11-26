"""
Appointments page - Schedule and manage patient appointments

This page will allow:
- Viewing upcoming appointments
- Scheduling new appointments
- Canceling/rescheduling appointments
- Filtering by date, patient, specialty
"""
import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Appointments - Patient Triage System",
    page_icon="📅",
    layout="wide",
)

st.title("📅 Appointments")
st.markdown("---")

# Placeholder for Phase 3+
st.info("📅 Appointment scheduling will be available in Phase 3")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("## Upcoming Appointments")
    st.info("No appointments scheduled")

with col2:
    st.markdown("## Schedule New Appointment")
    st.date_input("Date", value=datetime.now())
    st.time_input("Time", value=datetime.now().time())
    st.text_input("Patient ID", placeholder="Enter patient ID")
    st.selectbox("Specialty", ["General Medicine", "Cardiology", "Neurology", "Orthopedics"])
    st.button("Schedule Appointment", disabled=True)
