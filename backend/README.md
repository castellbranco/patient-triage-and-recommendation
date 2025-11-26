# Patient Triage Backend

FastAPI backend following Clean Architecture principles for the Patient Triage & Management System.

## Architecture

This backend implements **Clean Architecture** with four distinct layers:

### Domain Layer (`app/domain/`)
- **Entities**: Core business objects (User, Patient, Appointment, etc.)
- **Value Objects**: Immutable values (Email, PhoneNumber, ICD10Code, etc.)
- **Exceptions**: Domain-specific exceptions
- **No external dependencies**: Pure Python business logic

### Application Layer (`app/application/`)
- **Use Cases**: Business logic orchestration (RegisterPatient, TriageSymptoms, etc.)
- **DTOs**: Data Transfer Objects for request/response
- **Interfaces**: Abstract interfaces (Repository protocols, external services)

### Infrastructure Layer (`app/infrastructure/`)
- **Database**: SQLAlchemy models, connection management
- **Repositories**: Concrete implementations of repository interfaces
- **External**: Third-party API adapters (NLM Medical Conditions API)
- **Config**: Application configuration using pydantic-settings

### Presentation Layer (`app/presentation/`)
- **API Routes**: FastAPI endpoints
  - `api/public/v1/`: Public, versioned endpoints
  - `api/internal/`: Internal, non-versioned endpoints
- **Dependencies**: FastAPI dependency injection

### Shared Layer (`app/shared/`)
- **Utils**: Shared utilities across layers
- **Constants**: Application-wide constants

## Setup

### Prerequisites
- Python 3.11+
- PDM (Python package manager)
- PostgreSQL 15+ (or use Docker Compose)

### Installation

```bash
# Install PDM if not already installed
pip install pdm

# Install dependencies (including dev dependencies)
pdm install -d

# Or install only production dependencies
pdm install --prod
```

### Environment Configuration

Copy the root `.env.example` to `.env` and configure:

```bash
cp ../.env.example ../.env
```

Key environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key (generate with `openssl rand -hex 32`)
- `BACKEND_CORS_ORIGINS`: Allowed CORS origins

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description of changes"

# Apply migrations
pdm run migrate

# Or manually
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Running the Server

```bash
# Development server with hot-reload
pdm run dev

# Or manually
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Access the API:
- API Documentation: http://localhost:8000/docs
- ReDoc Documentation: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/openapi.json
- Health Check: http://localhost:8000/api/public/v1/health

## Development

### Code Quality

```bash
# Run linter
pdm run lint

# Format code
pdm run format

# Type checking
pdm run typecheck
```

### Testing

```bash
# Run all tests (Phase 1+)
pdm run pytest

# Run with coverage
pdm run pytest --cov=app --cov-report=html

# Run specific test file
pdm run pytest tests/unit/test_example.py
```

### PDM Scripts

Available scripts in `pyproject.toml`:

- `pdm run dev`: Start development server
- `pdm run migrate`: Apply database migrations
- `pdm run migration "message"`: Create new migration
- `pdm run lint`: Run ruff linter
- `pdm run format`: Format code with black
- `pdm run typecheck`: Type check with mypy

## API Structure

### Public Endpoints (Versioned)

```
/api/public/v1/health      # Health check
/api/public/v1/ready       # Readiness check
# Future endpoints will be added in Phase 1+
```

### Internal Endpoints (Not Versioned)

```
/api/internal/auth         # Authentication (Phase 1)
# Internal endpoints can evolve freely without versioning
```

## Project Structure

```
backend/
├── src/
│   └── app/
│       ├── main.py                  # FastAPI application entry
├── tests/
│   ├── unit/                        # Unit tests
│   ├── integration/                 # Integration tests
│   └── e2e/                         # End-to-end tests
├── scripts/                         # Utility scripts
├── alembic/                         # Database migrations
│   └── versions/                    # Migration files
├── alembic.ini                      # Alembic configuration
└── Dockerfile                       # Container image
```

## Dependency Injection

This project uses **Dishka** for dependency injection (ADR-002).

Dishka provides:
- Framework-agnostic DI
- Type-safe dependency resolution
- Async support
- Scope management

Implementation will be added in Phase 1.

## External Integrations

### NLM Medical Conditions API (Phase 2)

Integration with the National Library of Medicine Clinical Tables API for:
- Symptom validation against ICD-10 codes
- Medical condition standardization
- Autocomplete for symptom entry

Adapter location: `app/infrastructure/external/nlm_client.py`

## Development Phases

This backend evolves through tagged releases:

- **v0.1.0-mvp** (Current): Foundation, Auth, Database
- **v0.2.0-triage-core**: NLM API Integration, Triage Logic
- **v0.3.0-security**: RBAC, Audit Logging, Security Headers
- **v0.4.0-clinical**: Medical Records, Prescriptions, Vital Signs
- **v0.5.0-scale**: Redis Caching, Pagination, Background Tasks
- **v0.6.0-production**: Observability, Monitoring, Production Readiness

See [../ROADMAP.md](../ROADMAP.md) for complete progression.

## Contributing

1. Follow Clean Architecture principles
2. Keep layers separated and dependencies pointing inward
3. Write tests for new functionality
4. Ensure code passes linting and type checking
5. Format code before committing

## License

MIT License
