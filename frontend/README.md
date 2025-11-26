# Patient Triage Frontend

Streamlit-based user interface for the Patient Triage & Management System.

## Overview

This frontend provides a web-based interface for healthcare professionals to:
- Register and manage patients
- Perform automated symptom triage
- Schedule appointments
- View medical records
- Generate reports

Built with **Streamlit** for rapid development, with plans to migrate to **React + TypeScript** for enhanced scalability and performance.

## Technology Stack

- **Framework**: Streamlit 1.29+
- **HTTP Client**: Requests
- **Environment**: python-dotenv
- **Validation**: Pydantic
- **Future**: React + TypeScript (Phase 4+)

## Setup

### Prerequisites
- Python 3.11+
- PDM (Python package manager)
- Backend API running (see [../backend/README.md](../backend/README.md))

### Installation

```bash
# Install dependencies
pdm install

# Or install only production dependencies
pdm install --prod
```

### Environment Configuration

The frontend reads configuration from the root `.env` file:

```bash
# Ensure root .env file exists
cp ../.env.example ../.env
```

Key environment variables:
- `BACKEND_API_URL`: Backend API endpoint (default: http://localhost:8000)
- `FRONTEND_PORT`: Streamlit port (default: 8501)

### Running the Application

```bash
# Start Streamlit server
pdm run start

# Or manually
streamlit run app.py --server.port 8501
```

Access the application:
- Frontend: http://localhost:8501
- Streamlit runs on port 8501 by default

## Project Structure

```
frontend/
├── app.py                    # Main Streamlit application entry
├── pages/                    # Streamlit multi-page app
│   ├── dashboard.py    # Dashboard overview
│   ├── profile.py      # User profile management
│   └── appointments.py # Appointment scheduling
├── components/               # Reusable Streamlit components
│   └── __init__.py
├── shared/                   # Shared utilities
│   ├── api_client.py        # Backend API client
│   └── auth.py              # Authentication utilities
├── tests/                    # Frontend tests
├── scripts/                  # Utility scripts
├── Dockerfile               # Container image
└── README.md                # This file
```

## Development

### Code Quality

```bash
# Format code
pdm run black .

# Lint code
pdm run ruff check .
```

### Streamlit Features

#### Multi-Page App
Streamlit automatically detects pages in the `pages/` directory:
- Files are sorted alphabetically
- Emojis in filenames create icons in sidebar
- Navigation is automatic

#### Session State
Use `st.session_state` for managing user state:
```python
st.session_state.authenticated = True
st.session_state.user = user_data
```

#### Custom Styling
Add custom CSS with `st.markdown()`:
```python
st.markdown("""
<style>
    .custom-class { color: blue; }
</style>
""", unsafe_allow_html=True)
```

## API Client

The `shared/api_client.py` module provides a centralized client for backend communication:

```python
from shared.api_client import api_client

# Check backend health
health = api_client.health_check()

# Authenticate (Phase 1)
# response = api_client.login(email, password)
```

## Authentication

Authentication utilities in `shared/auth.py`:

```python
from shared.auth import require_auth, is_authenticated, logout

# Require authentication for a page
require_auth()

# Check if user is logged in
if is_authenticated():
    st.write(f"Welcome, {get_current_user()['name']}")
```

Note: Authentication will be fully implemented in Phase 1.

## Docker Deployment

```bash
# Build frontend image
docker build -t patient-triage-frontend .

# Run container
docker run -p 8501:8501 \
  -e BACKEND_API_URL=http://backend:8000 \
  patient-triage-frontend
```

Or use Docker Compose from root:

```bash
docker-compose up frontend
```

## Development Phases

### Current (v0.1.0-mvp)
- ✅ Basic Streamlit structure
- ✅ Multi-page navigation
- ✅ API client scaffold
- ✅ Authentication scaffold

### Phase 1 (v0.1.0-mvp)
- 🔄 User authentication UI
- 🔄 Patient registration form
- 🔄 Dashboard with metrics

### Phase 2 (v0.2.0-triage-core)
- 📋 Symptom entry with NLM autocomplete
- 🩺 Triage results visualization
- 📊 Vital signs input

### Phase 3 (v0.3.0-security)
- 🔐 Role-based UI elements
- 📜 Audit log viewer

### Phase 4 (v0.4.0-clinical)
- 📋 Medical records display
- 💊 Prescription management
- 📈 Vital signs charts

### Future
- 🚀 Migration to React + TypeScript
- 📱 Mobile-responsive design
- ♿ Accessibility improvements

## Streamlit Configuration

Create `.streamlit/config.toml` for custom configuration:

```toml
[server]
port = 8501
address = "0.0.0.0"
headless = true

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

## Future Migration to React

When migrating to React + TypeScript:
- Keep API client interface consistent
- Reuse authentication flow
- Maintain same API endpoints
- Use Streamlit as reference for UI/UX

## Contributing

1. Follow Streamlit best practices
2. Keep components modular and reusable
3. Use session state appropriately
4. Format code before committing
5. Test backend integration

## Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Gallery](https://streamlit.io/gallery)
- [Multi-page Apps](https://docs.streamlit.io/library/get-started/multipage-apps)

## License

MIT License
