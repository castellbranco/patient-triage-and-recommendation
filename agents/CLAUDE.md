# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Patient Triage & Management System** that demonstrates production-grade healthcare backend development. The core differentiator is **symptom standardization** through integration with the **NLM (National Library of Medicine) Medical Conditions API** to validate patient inputs against official ICD-10 codes.

The project is a **monorepo** with:
- **Backend**: FastAPI application following Clean Architecture
- **Frontend**: Streamlit UI (with planned migration to React + TypeScript)

## Development Commands

### Package Manager
This project uses **PDM** for dependency management. All commands run from the repository root.

### Installation
```bash
# Install all dependencies (backend + frontend)
pdm install

# Install production dependencies only
pdm install --prod

# Install with dev dependencies
pdm install -d
```

### Running Services

#### Local Development (Without Docker)
```bash
# Start backend (with hot-reload)
pdm run dev-backend

# Start backend in production mode (4 workers)
pdm run dev-backend-prod

# Start frontend
pdm run dev-frontend
```

#### Docker Development
```bash
# Start all services (PostgreSQL + Backend + Frontend)
pdm run docker-up

# View logs
pdm run docker-logs

# Stop services
pdm run docker-down

# Rebuild images
pdm run docker-build

# Stop and remove volumes
pdm run docker-clean
```

### Database Operations
```bash
# Apply all pending migrations
pdm run migrate

# Create a new migration (auto-generated from models)
pdm run migrate-create "description of changes"

# Rollback one migration
pdm run migrate-down

# View migration history
pdm run migrate-history
```

**Note**: Migrations are managed with Alembic and should be created from the `backend/` directory context.

### Code Quality
```bash
# Linting
pdm run lint              # Check code with ruff
pdm run lint-fix          # Auto-fix linting issues

# Formatting
pdm run format            # Format code with black
pdm run format-check      # Check formatting without changes

# Type Checking
pdm run typecheck         # Run mypy type checker
```

**Standards**:
- Line length: 100 characters
- Python version: 3.11+
- Black for formatting
- Ruff for linting
- MyPy for type checking (strict mode for backend)

### Testing
```bash
# Run all tests
pdm run test

# Run tests with coverage report
pdm run test-cov

# Run tests in watch mode
pdm run test-watch

# Run specific test file
cd backend && pytest tests/unit/test_example.py
```

**Test Structure**:
- `backend/tests/unit/` - Unit tests
- `backend/tests/integration/` - Integration tests
- `backend/tests/e2e/` - End-to-end tests

### Security
```bash
# Run security scanner
pdm run security-check

# Check dependencies for vulnerabilities
pdm run security-deps
```

### CI/CD Simulation
```bash
# Run backend CI checks (lint + typecheck + test)
pdm run ci-backend

# Run all CI checks
pdm run ci-all
```

## Architecture

### Clean Architecture Layers

This project strictly follows **Clean Architecture** principles with dependency flow **inward only**:

```
Presentation Layer (Outermost)
    ↓
Infrastructure Layer
    ↓
Application Layer
    ↓
Domain Layer (Innermost)
```

#### 1. Domain Layer (`backend/src/app/domain/`)
- **Purpose**: Core business entities and rules
- **Contains**: Entities, Value Objects, Domain Exceptions
- **Rules**:
  - No external dependencies
  - Pure Python business logic
  - No framework imports
  - Rich domain models with behavior

#### 2. Application Layer (`backend/src/app/application/`)
- **Purpose**: Business logic orchestration (use cases)
- **Contains**: Use Cases, DTOs, Interfaces (Protocols)
- **Rules**:
  - Can depend on Domain layer only
  - Defines abstract interfaces for infrastructure
  - Contains application-specific business rules
  - No framework or database code

#### 3. Infrastructure Layer (`backend/src/app/infrastructure/`)
- **Purpose**: External system implementations
- **Contains**: Database (SQLAlchemy models), Repositories, External API adapters, Configuration
- **Rules**:
  - Implements interfaces defined in Application layer
  - All external dependencies live here
  - Framework-specific code (SQLAlchemy, httpx, etc.)

#### 4. Presentation Layer (`backend/src/app/presentation/`)
- **Purpose**: API endpoints and request/response handling
- **Contains**: FastAPI routers, Dependencies, Serialization
- **Structure**:
  - `api/public/v1/` - Public, versioned endpoints
  - `api/internal/` - Internal, non-versioned endpoints
- **Rules**:
  - Thin layer that delegates to use cases
  - No business logic
  - Handles HTTP concerns only

### Dependency Injection

This project uses **Dishka** for dependency injection (see [docs/decisions/ADR-002-dishka-di.md](docs/decisions/ADR-002-dishka-di.md)).

**Key Points**:
- Framework-agnostic DI
- Type-safe with MyPy support
- Async-first design
- Scoped lifetimes: `APP` (singleton), `REQUEST` (per-request)
- Use `FromDishka[T]` in FastAPI routes to inject dependencies

**Example**:
```python
from dishka.integrations.fastapi import FromDishka

@router.post("/patients")
async def register_patient(
    dto: RegisterPatientRequest,
    use_case: FromDishka[RegisterPatientUseCase],
):
    return await use_case.execute(dto)
```

### External Integrations

#### NLM Medical Conditions API
- **Purpose**: Symptom validation and ICD-10 code lookup
- **Base URL**: `https://clinicaltables.nlm.nih.gov`
- **Implementation**: `app/infrastructure/external/nlm_client.py` (Phase 2)
- **Pattern**: Adapter pattern - abstracts external API behind `INLMClient` interface

## Project Progression

This repository uses **annotated git tags** to demonstrate progressive development stages. **Do not look for feature branches**. Checkout specific tags to see the codebase at each maturity level:

- **v0.1.0-mvp**: Foundation (FastAPI, PostgreSQL, JWT Auth)
- **v0.2.0-triage-core**: NLM API Integration & Triage Engine
- **v0.3.0-security**: RBAC, Audit Logging, Security Headers
- **v0.4.0-clinical**: Medical Records & Complex Entities
- **v0.5.0-scale**: Redis Caching & Performance Optimization
- **v0.6.0-production**: Observability & Production Readiness

See [ROADMAP.md](ROADMAP.md) for the complete 12-week development plan.

## Important Patterns & Conventions

### Repository Pattern
All data access is abstracted behind repository interfaces:
```python
# Application layer defines interface
class IPatientRepository(Protocol):
    async def save(self, patient: Patient) -> Patient: ...
    async def find_by_id(self, id: UUID) -> Optional[Patient]: ...

# Infrastructure implements it
class SQLAlchemyPatientRepository(IPatientRepository):
    # Implementation with SQLAlchemy
```

### Use Case Pattern
Each feature is implemented as a use case:
```python
class RegisterPatientUseCase:
    def __init__(self, patient_repo: IPatientRepository):
        self.patient_repo = patient_repo

    async def execute(self, dto: RegisterPatientDTO) -> Patient:
        # Orchestrate business logic
        ...
```

### Value Objects
Validation is encapsulated in immutable value objects:
```python
class Email:
    def __init__(self, value: str):
        if not self._is_valid(value):
            raise InvalidEmailError(value)
        self.value = value
```

### API Versioning
- **Public endpoints** (`/api/public/v1/...`): Versioned for backwards compatibility
- **Internal endpoints** (`/api/internal/...`): Not versioned, can evolve freely

## Environment Configuration

All configuration is managed through environment variables. Copy `.env.example` to `.env` and configure:

**Key Variables**:
- `DATABASE_URL`: PostgreSQL connection string (async driver: `postgresql+asyncpg://...`)
- `SECRET_KEY`: JWT signing key (generate with `openssl rand -hex 32`)
- `BACKEND_CORS_ORIGINS`: JSON array of allowed CORS origins
- `NLM_API_BASE_URL`: NLM Clinical Tables API base URL
- `ENVIRONMENT`: `development`, `staging`, or `production`

**Never commit `.env` or `.env.docker` files**.

## Database

### Technology
- **Database**: PostgreSQL 15+
- **Driver**: AsyncPG (async driver)
- **ORM**: SQLAlchemy 2.0 (Async)
- **Migrations**: Alembic

### Connection String Format
```
postgresql+asyncpg://user:password@host:port/database
```

### Migration Workflow
1. Modify SQLAlchemy models in `backend/src/app/infrastructure/database/models/`
2. Generate migration: `pdm run migrate-create "description"`
3. Review generated migration in `backend/alembic/versions/`
4. Apply migration: `pdm run migrate`

## Docker Services

The `docker-compose.yml` defines three services:

1. **postgres**: PostgreSQL 15 database
   - Port: 5432
   - Health check: `pg_isready`
   - Volume: `postgres_data`

2. **backend**: FastAPI application
   - Port: 8000
   - Depends on: postgres
   - Command: `uvicorn app.main:app --reload`
   - Health check: `/api/public/v1/health`

3. **frontend**: Streamlit application
   - Port: 8501
   - Depends on: backend
   - Command: `streamlit run app.py`

All services communicate via the `triage-network` bridge network.

## Anti-Patterns to Avoid

When working on this codebase:

❌ **Don't** put business logic in API routes (Presentation layer)
❌ **Don't** let Domain layer import from Infrastructure or Presentation
❌ **Don't** create circular dependencies between layers
❌ **Don't** bypass use cases and call repositories directly from routes
❌ **Don't** mix concerns (e.g., SQLAlchemy code in use cases)
❌ **Don't** use synchronous database operations (use async/await)
❌ **Don't** import from outer layers in inner layers

✅ **Do** follow the dependency rule (dependencies point inward)
✅ **Do** use interfaces (Protocols) for abstraction
✅ **Do** encapsulate validation in Value Objects
✅ **Do** keep use cases focused on single responsibilities
✅ **Do** use type hints everywhere (required for MyPy and Dishka)

## Current Status

The project is currently at the **skeleton/MVP stage** (pre-v0.1.0):
- Basic FastAPI application structure
- Main entry point with lifespan management
- CORS middleware configured
- Health check endpoint structure (implementation pending)
- Directory structure for Clean Architecture layers
- Docker Compose configuration
- PDM scripts for common operations

**Next steps** (Phase 1 - v0.1.0-mvp):
- Implement Domain entities (User, Patient)
- Set up PostgreSQL connection with SQLAlchemy
- Implement JWT authentication
- Create user registration and login endpoints
- Set up Dishka dependency injection container
- Add initial database migrations

## Additional Resources

- [Clean Architecture Documentation](docs/architecture/clean-architecture.md)
- [ADR-001: PostgreSQL](docs/decisions/ADR-001-postgresql.md)
- [ADR-002: Dishka DI](docs/decisions/ADR-002-dishka-di.md)
- [ADR-005: NLM API](docs/decisions/ADR-005-nlm-api.md)
- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)