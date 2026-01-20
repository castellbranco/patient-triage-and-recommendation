# Documentation

Welcome to the Patient Triage & Management System documentation.

## Getting Started

For setup and development instructions, see the main [README.md](../README.md) in the project root.

## Architecture

This project follows **Clean Architecture** principles:

- **Domain Layer**: Core business entities and rules (no external dependencies)
- **Application Layer**: Use cases and business logic orchestration
- **Infrastructure Layer**: Database, external APIs, and framework implementations
- **Presentation Layer**: API endpoints and request/response handling

```
Presentation → Infrastructure → Application → Domain
(Outermost)                                   (Innermost)
```

### Key Principles

- Dependencies point inward only
- Inner layers are independent of outer layers
- Business logic is independent of frameworks and databases
- Everything is testable in isolation

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Quick API Test

```bash
# Health check
curl http://localhost:8000/api/public/v1/health

# Analyze symptoms (example)
curl -X POST "http://localhost:8000/api/v1/triage/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "123e4567-e89b-12d3-a456-426614174000",
    "symptoms": "headache and fever"
  }'
```

## Database

- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic

```bash
# Run migrations
pdm run migrate

# Create new migration
pdm run migrate-create "description"
```

## Testing

```bash
# Run all tests
pdm run test

# Run with coverage
pdm run test-cov
```

## Contributing

1. Follow Clean Architecture principles
2. Write tests for new features
3. Run linting and formatting before commits:
   ```bash
   pdm run lint-fix
   pdm run format
   ```
4. Keep commits focused and descriptive

## Technology Stack

- **Backend**: FastAPI, SQLAlchemy, Dishka (DI)
- **Database**: PostgreSQL + asyncpg
- **Testing**: pytest + pytest-asyncio
- **Code Quality**: ruff, black, mypy
- **External APIs**: NLM Clinical Tables API

## Project Structure

```
backend/src/
├── domain/          # Business entities and rules
├── infrastructure/  # External systems (DB, APIs)
│   ├── api/        # FastAPI routes
│   ├── database/   # SQLAlchemy models
│   ├── repo/       # Repository implementations
│   └── ext/        # External API clients
└── services/       # Business logic (use cases)
```

## License

MIT License - See [LICENSE](../LICENSE) for details.
