# Contributing Guide

Thank you for considering contributing to the Patient Triage & Management System!

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/patient-triage-and-recommendation.git
   cd patient-triage-and-recommendation
   ```

2. **Install dependencies**
   ```bash
   pdm install
   ```

3. **Start services**
   ```bash
   pdm run docker-up
   ```

## Code Style

We use automated tools to maintain code quality:

- **Formatting**: Black (100 char line length)
- **Linting**: Ruff
- **Type Checking**: MyPy (strict mode)

Before committing:
```bash
pdm run format      # Format code
pdm run lint-fix    # Fix linting issues
pdm run typecheck   # Check types
```

## Architecture Guidelines

Follow Clean Architecture principles:

### ✅ DO
- Keep business logic in the domain/service layers
- Use dependency injection (Dishka)
- Write unit tests for business logic
- Use type hints everywhere
- Implement interfaces (Protocols) for dependencies
- Keep API routes thin (delegate to services)

### ❌ DON'T
- Put business logic in API routes
- Import from outer layers in inner layers
- Use synchronous database operations
- Bypass repositories to access the database directly
- Create circular dependencies

## Testing

Write tests for all new features:

```bash
# Run tests
pdm run test

# Run specific test file
cd backend && pytest tests/unit/test_example.py -v

# Run with coverage
pdm run test-cov
```

Test structure:
- `backend/tests/unit/` - Unit tests (isolated)
- `backend/tests/integration/` - Integration tests (with DB)
- `backend/tests/e2e/` - End-to-end tests

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make your changes**
   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation if needed

3. **Verify your changes**
   ```bash
   pdm run ci-backend  # Runs lint, typecheck, and tests
   ```

4. **Commit with clear messages**
   ```bash
   git commit -m "feat: add symptom severity scoring"
   ```

5. **Push and create PR**
   ```bash
   git push origin feat/your-feature-name
   ```

## Commit Message Format

Use conventional commits:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding/updating tests
- `chore:` - Maintenance tasks

Examples:
```
feat: add patient appointment scheduling
fix: resolve timezone issue in triage results
docs: update API testing guide
```

## Database Migrations

When modifying database models:

1. Update SQLAlchemy models in `backend/src/infrastructure/database/models/`
2. Create migration:
   ```bash
   pdm run migrate-create "description of changes"
   ```
3. Review generated migration in `backend/alembic/versions/`
4. Test migration:
   ```bash
   pdm run migrate      # Apply
   pdm run migrate-down # Rollback to test
   pdm run migrate      # Reapply
   ```

## Questions?

- Open an issue for bugs or feature requests
- Check existing issues before creating new ones
- Be respectful and constructive in discussions

Thank you for contributing! 🙏
