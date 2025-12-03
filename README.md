# Patient Triage & Management System

A production-grade healthcare backend system demonstrating **symptom standardization** through integration with the **NLM Medical Conditions API**, powering an automated triage and recommendation engine.

## Overview

This project solves the problem of symptom standardization by integrating with the NLM (National Library of Medicine) Medical Conditions API to validate patient inputs against official ICD-10 codes. The system provides automated triage capabilities and specialty recommendations based on standardized medical data.

**See [ROADMAP.md](ROADMAP.md)** for the complete 12-week development progression from MVP to production-ready system.

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+ with AsyncPG
- **ORM**: SQLAlchemy 2.0 (Async)
- **Dependency Management**: PDM
- **Migrations**: Alembic
- **DI Framework**: Dishka
- **Authentication**: JWT (python-jose + passlib)
- **Validation**: Pydantic V2

### Frontend
- **Current**: Streamlit (Python)
- **Future**: React + TypeScript (planned)

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **IaC**: Terraform (GCP/AWS)
- **Future**: Redis (Phase 5), OpenTelemetry (Phase 6)

## Architecture

This project follows **Clean Architecture** principles with clear separation of concerns:

```
Domain Layer       → Core business entities and rules (no external dependencies)
Application Layer  → Use cases and business logic orchestration
Infrastructure     → External systems (database, APIs, repositories)
Presentation       → API endpoints and request/response handling
```

Read more in [docs/architecture/clean-architecture.md](docs/architecture/clean-architecture.md)

## Monorepo Structure

```
patient-triage-and-recommendation/
├── backend/          # FastAPI application with Clean Architecture
├── frontend/         # Streamlit UI (future: React/TypeScript)
├── docs/             # Architecture decisions (ADRs) and guides
├── deploy/           # Docker, Kubernetes, Terraform configurations
├── .env.example      # Environment variables template
└── docker-compose.yml # Local development orchestration
```

## Quick Start

### Prerequisites
- Docker & Docker Compose (for containerized development)
- Python 3.11+ (for local development)
- PDM (Python package manager) - `pip install pdm`

### Option 1: Running with Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd patient-triage-and-recommendation
   ```

2. **Copy environment files**
   ```bash
   cp .env.example .env
   # Edit .env if needed for local configuration
   ```

3. **Start all services using PDM**
   ```bash
   # Install PDM if not already installed
   pip install pdm

   # Start all services (PostgreSQL + Backend + Frontend)
   pdm run docker-up

   # Or manually with docker-compose
   docker-compose up -d
   ```

4. **Access the applications**
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Frontend (Streamlit): http://localhost:8501
   - Health Check: http://localhost:8000/api/public/v1/health

5. **View logs**
   ```bash
   pdm run docker-logs
   ```

6. **Stop services**
   ```bash
   pdm run docker-down
   ```

### Option 2: Local Development (Without Docker)

1. **Install dependencies** (one command for the entire monorepo)
   ```bash
   # Install PDM if not already installed
   pip install pdm

   # Install all dependencies (backend + frontend)
   pdm install
   ```

2. **Copy and configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

3. **Run the setup script** (starts PostgreSQL, creates DB, runs migrations)
   ```bash
   pdm run setup
   ```

4. **Start backend and frontend** (in separate terminals)
   ```bash
   # Terminal 1: Start backend
   pdm run dev-backend

   # Terminal 2: Start frontend
   pdm run dev-frontend
   ```

## Development Workflow

### Available PDM Scripts

The monorepo uses a single `pyproject.toml` at the root with PDM scripts for all operations:

#### Development Servers

```bash
# Backend (FastAPI)
pdm run dev-backend          # Start backend with hot-reload
pdm run dev-backend-prod     # Start backend in production mode (4 workers)

# Frontend (Streamlit)
pdm run dev-frontend         # Start Streamlit frontend

# All services (requires Docker)
pdm run dev-all              # Start all services with docker-compose
```

#### Database Operations

```bash
pdm run init-db              # Create database (run once on first setup)
pdm run migrate              # Apply all pending migrations
pdm run migrate-create "message"  # Create new migration
pdm run migrate-down         # Rollback one migration
pdm run migrate-history      # View migration history
pdm run db-shell             # Open psql shell to database
```

#### Code Quality

```bash
# Linting
pdm run lint                 # Check code with ruff
pdm run lint-fix             # Auto-fix linting issues

# Formatting
pdm run format               # Format code with black
pdm run format-check         # Check formatting without changes

# Type Checking
pdm run typecheck            # Run mypy type checker
```

#### Testing

```bash
pdm run test                 # Run all tests
pdm run test-cov             # Run tests with coverage report
pdm run test-watch           # Run tests in watch mode
```

#### Security

```bash
pdm run security-check       # Run bandit security scanner
pdm run security-deps        # Check dependencies for vulnerabilities
```

#### Docker Operations

```bash
pdm run docker-up            # Start all Docker services
pdm run docker-down          # Stop all Docker services
pdm run docker-logs          # View logs from all services
pdm run docker-build         # Rebuild Docker images
pdm run docker-clean         # Stop and remove volumes
```

#### Installation

```bash
pdm install                  # Install all dependencies
pdm install --prod           # Install production dependencies only
pdm install -d               # Install with dev dependencies
```

#### CI/CD Simulation

```bash
pdm run ci-backend           # Run backend CI checks (lint + typecheck + test)
pdm run ci-all               # Run all CI checks
```

### Database Migrations

```bash
# Create a new migration
cd backend
alembic revision --autogenerate -m "description"

# Apply migrations
pdm run migrate

# Or manually
alembic upgrade head
```

## Project Progression

This repository uses **annotated git tags** to demonstrate progressive development:

- **v0.1.0-mvp**: Foundation (FastAPI, PostgreSQL, JWT Auth)
- **v0.2.0-triage-core**: NLM API Integration & Triage Engine
- **v0.3.0-security**: RBAC, Audit Logging, Security Headers
- **v0.4.0-clinical**: Medical Records & Complex Entities
- **v0.5.0-scale**: Redis Caching & Performance Optimization
- **v0.6.0-production**: Observability & Production Readiness

**Checkout specific tags** to see the codebase at each stage of maturity.

## API Structure

### Public Endpoints (Versioned)
```
/api/public/v1/health      # Health check
/api/public/v1/...         # Other public endpoints
```

### Internal Endpoints (Not Versioned)
```
/api/internal/auth         # Authentication endpoints
/api/internal/...          # Other internal endpoints
```

Public endpoints use versioning for backwards compatibility. Internal endpoints can evolve freely.

## Documentation

- [ROADMAP.md](ROADMAP.md) - Complete 12-week development plan
- [Backend README](backend/README.md) - Backend setup and architecture
- [Frontend README](frontend/README.md) - Frontend development guide
- [docs/](docs/) - Architecture decisions, API docs, deployment guides

## Key Architecture Decisions (ADRs)

- [ADR-001: PostgreSQL for Relational Data](docs/decisions/ADR-001-postgresql.md)
- [ADR-002: Dishka for Dependency Injection](docs/decisions/ADR-002-dishka-di.md)
- [ADR-005: NLM API for Symptom Validation](docs/decisions/ADR-005-nlm-api.md)

## Environment Variables

All configuration is managed through environment variables. See `.env.example` for a comprehensive list with descriptions.

**Important**: Never commit `.env` or `.env.docker` files to version control.

## Contributing

This is a demonstration project showcasing backend development best practices. Contributions are welcome!

1. Follow the existing Clean Architecture patterns
2. Ensure code passes linting (`pdm run lint`)
3. Format code with black (`pdm run format`)
4. Type check with mypy (`pdm run typecheck`)
5. Update documentation as needed

## License

[MIT License](LICENSE)

## Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [NLM Clinical Tables API](https://clinicaltables.nlm.nih.gov/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

---

**Built with FastAPI, PostgreSQL, and Clean Architecture principles**
