# Documentation

Comprehensive documentation for the Patient Triage & Management System.

## Contents

### Architecture Documentation
- [Clean Architecture Overview](architecture/clean-architecture.md)
- [Data Flow Diagrams](architecture/data-flow.md)
- [System Diagrams](architecture/diagrams/)

### Architecture Decision Records (ADRs)
- [ADR-001: PostgreSQL for Relational Data](decisions/ADR-001-postgresql.md)
- [ADR-002: Dishka for Dependency Injection](decisions/ADR-002-dishka-di.md)
- [ADR-005: NLM API for Symptom Validation](decisions/ADR-005-nlm-api.md)

### API Documentation
- [OpenAPI Specification](api/openapi.md)
- Auto-generated docs available at `/docs` endpoint

### Deployment Guides
- [Docker Deployment](deployment/docker.md)
- [GCP Deployment](deployment/gcp.md)
- [AWS Deployment](deployment/aws.md)

## Quick Links

- [Backend README](../backend/README.md)
- [Frontend README](../frontend/README.md)
- [Project ROADMAP](../ROADMAP.md)
- [Main README](../README.md)

## Documentation Standards

### ADR Format
All architectural decisions should be documented using the ADR template:

1. **Status**: Proposed, Accepted, Deprecated, Superseded
2. **Context**: What is the issue/situation?
3. **Decision**: What decision was made?
4. **Consequences**: What are the implications?
5. **Alternatives**: What other options were considered?

### Naming Convention
- ADRs: `ADR-XXX-short-description.md`
- Architecture docs: `descriptive-name.md`
- Keep filenames lowercase with hyphens

## Contributing Documentation

When adding new features or making architectural changes:

1. Update relevant documentation
2. Create new ADR if architectural decision is made
3. Update diagrams if system structure changes
4. Keep OpenAPI spec in sync with API changes
