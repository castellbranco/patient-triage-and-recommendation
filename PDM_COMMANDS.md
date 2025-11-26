# PDM Commands Quick Reference

This monorepo uses a single `pyproject.toml` at the root for managing all dependencies (backend + frontend).

## Installation

```bash
# Install PDM globally
pip install pdm

# Install all project dependencies
pdm install

# Install only production dependencies
pdm install --prod

# Install with dev dependencies
pdm install -d
```

## Development Servers

### Backend (FastAPI)

```bash
# Development mode with hot-reload
pdm run dev-backend

# Production mode with 4 workers
pdm run dev-backend-prod
```

Access: http://localhost:8000
API Docs: http://localhost:8000/docs

### Frontend (Streamlit)

```bash
# Start Streamlit frontend
pdm run dev-frontend
```

Access: http://localhost:8501

### All Services (Docker)

```bash
# Start PostgreSQL + Backend + Frontend
pdm run dev-all

# Or use docker-compose directly
docker-compose up
```

## Database Operations

```bash
# Apply all pending migrations
pdm run migrate

# Create a new migration
pdm run migrate-create "add user table"

# Rollback one migration
pdm run migrate-down

# View migration history
pdm run migrate-history
```

## Code Quality

### Linting

```bash
# Check code with ruff
pdm run lint

# Auto-fix linting issues
pdm run lint-fix
```

### Formatting

```bash
# Format code with black
pdm run format

# Check formatting without making changes
pdm run format-check
```

### Type Checking

```bash
# Run mypy type checker on backend
pdm run typecheck
```

## Testing

```bash
# Run all tests
pdm run test

# Run tests with coverage report
pdm run test-cov

# Run tests in watch mode (auto-rerun on changes)
pdm run test-watch
```

## Security

```bash
# Run bandit security scanner on backend code
pdm run security-check

# Check dependencies for known vulnerabilities
pdm run security-deps
```

## Docker Operations

```bash
# Start all services (detached)
pdm run docker-up

# Stop all services
pdm run docker-down

# View logs from all services
pdm run docker-logs

# Rebuild Docker images
pdm run docker-build

# Stop and remove volumes (clean slate)
pdm run docker-clean
```

## CI/CD Simulation

```bash
# Run backend CI checks (lint + typecheck + test)
pdm run ci-backend

# Run all CI checks
pdm run ci-all
```

## Common Workflows

### First-Time Setup

```bash
# 1. Install PDM
pip install pdm

# 2. Install dependencies
pdm install -d

# 3. Copy environment file
cp .env.example .env

# 4. Start PostgreSQL (Docker)
docker run -d --name triage-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=triage_db \
  -p 5432:5432 postgres:15-alpine

# 5. Run migrations
pdm run migrate

# 6. Start backend
pdm run dev-backend

# 7. In another terminal, start frontend
pdm run dev-frontend
```

### Daily Development

```bash
# Start all services with Docker
pdm run docker-up

# View logs
pdm run docker-logs

# When done
pdm run docker-down
```

### Before Committing

```bash
# Format code
pdm run format

# Check linting
pdm run lint

# Run type check
pdm run typecheck

# Run tests
pdm run test

# Or run all CI checks at once
pdm run ci-backend
```

### Creating a New Migration

```bash
# 1. Modify SQLAlchemy models in backend/src/app/infrastructure/database/

# 2. Create migration
pdm run migrate-create "description of changes"

# 3. Review generated migration in backend/alembic/versions/

# 4. Apply migration
pdm run migrate
```

## Troubleshooting

### PDM Not Found

```bash
pip install --upgrade pdm
```

### Dependencies Out of Sync

```bash
# Remove lock file and reinstall
rm pdm.lock
pdm install
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check connection string in .env
cat .env | grep DATABASE_URL
```

### Port Already in Use

```bash
# Kill process on port 8000 (backend)
# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use different port
pdm run uvicorn app.main:app --port 8001
```

### Docker Issues

```bash
# Clean up everything
pdm run docker-clean

# Remove all containers and images
docker-compose down -v --rmi all

# Rebuild from scratch
pdm run docker-build
pdm run docker-up
```

## PDM Configuration

The `pyproject.toml` is located at the project root and includes:

- All backend dependencies (FastAPI, SQLAlchemy, etc.)
- All frontend dependencies (Streamlit, requests, etc.)
- All dev dependencies (pytest, black, ruff, mypy, etc.)
- PDM scripts for common operations
- Tool configurations (black, ruff, mypy, pytest)

## Adding New Dependencies

```bash
# Add production dependency
pdm add <package-name>

# Add dev dependency
pdm add -d <package-name>

# Add specific version
pdm add "package-name>=1.0.0"

# Example: Add a new library
pdm add httpx
```

## Updating Dependencies

```bash
# Update all dependencies
pdm update

# Update specific package
pdm update <package-name>

# Check outdated packages
pdm outdated
```

## Environment Variables

All environment variables are in the root `.env` file:

- `.env.example` - Template with all required variables
- `.env` - Your local configuration (gitignored)
- `.env.docker` - Docker Compose overrides

## Project Structure

```
patient-triage-and-recommendation/
├── pyproject.toml          # Single PDM configuration for entire monorepo
├── pdm.lock               # Locked dependencies
├── .env.example           # Environment template
├── backend/               # FastAPI backend
│   ├── src/
│   ├── tests/
│   └── alembic/
└── frontend/              # Streamlit frontend
    ├── app.py
    ├── pages/
    └── shared/
```

## Tips

1. **Always use PDM scripts** instead of running commands directly
2. **Single `pyproject.toml`** at root manages all dependencies
3. **No individual pyproject.toml** files in backend/ or frontend/
4. **Docker Compose** uses the root pyproject.toml via build context
5. **Migrations** are run from backend/ directory context
6. **Tests** are run from backend/tests/ directory

## Links

- [PDM Documentation](https://pdm.fming.dev/)
- [Project README](README.md)
- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)
- [ROADMAP](ROADMAP.md)
