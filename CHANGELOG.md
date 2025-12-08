# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-12-05

### Added
- **Phase 1 Complete**: Foundation & Core Infrastructure.
- **Authentication**: JWT-based auth (Login, Refresh, Me endpoints).
- **Database**: PostgreSQL schema with Users, Patients, Providers, Appointments.
- **API**: Full CRUD endpoints for all entities.
- **Infrastructure**:
    - Clean Architecture (API, Service, Repository layers).
    - Dishka Dependency Injection.
    - Alembic Migrations.
    - Docker Compose setup.
- **Testing**: Unit tests for Models, Schemas, Services, and API (71 tests passing).
- **Documentation**: Phase 1 completion report and Deployment guide.

### Changed
- Replaced `passlib` with direct `bcrypt` usage for compatibility.
- Updated database schema to include `updated_at` triggers.

### Fixed
- Database initialization issues in `init_db.py`.
- Auth service `UserNotActiveError` bug.
