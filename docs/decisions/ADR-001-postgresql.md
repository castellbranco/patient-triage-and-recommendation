# ADR-001: PostgreSQL for Relational Data Storage

**Status**: Accepted

**Date**: 2024-01-XX

**Deciders**: Development Team

## Context

The Patient Triage & Management System needs a robust, ACID-compliant database to handle:
- Patient records with complex relationships
- Medical history and vital signs
- Appointment scheduling
- Audit logging for compliance
- Triage results and recommendations

We need to choose a database that can:
1. Handle complex relational data (patients, appointments, medical records)
2. Ensure data consistency and integrity (ACID properties)
3. Support concurrent access from multiple users
4. Provide good performance for healthcare workloads
5. Integrate well with our Python/FastAPI stack

## Decision

We will use **PostgreSQL 15+** as our primary relational database.

## Rationale

### Why PostgreSQL?

1. **ACID Compliance**: Critical for healthcare data integrity
   - Transactions ensure data consistency
   - Prevents data corruption during concurrent updates

2. **Rich Data Types**: Supports complex healthcare data
   - JSONB for flexible medical data
   - Arrays for symptom lists
   - UUID for patient identifiers
   - Timestamp with timezone for accurate time tracking

3. **Performance**: Excellent for our use case
   - Efficient indexing (B-tree, GIN, GiST)
   - Query optimization and planner
   - Async support via asyncpg driver

4. **Async Support**: Integrates with FastAPI
   - AsyncPG driver for async operations
   - SQLAlchemy 2.0 async support
   - Non-blocking database operations

5. **Data Integrity**: Built-in constraints
   - Foreign keys for referential integrity
   - Check constraints for business rules
   - Triggers for complex validation

6. **Scalability**: Can grow with the system
   - Replication for read scaling
   - Partitioning for large tables
   - Connection pooling

7. **Ecosystem**: Mature tooling
   - Alembic for migrations
   - PgAdmin for management
   - Strong Python support

## Consequences

### Positive

✅ **Data Integrity**: ACID properties ensure medical data consistency
✅ **Rich Querying**: Complex SQL queries for analytics and reporting
✅ **Mature Ecosystem**: Well-tested tools and libraries
✅ **Async Performance**: Non-blocking operations with AsyncPG
✅ **Cost-Effective**: Open-source, no licensing costs
✅ **Cloud Support**: Available on GCP (Cloud SQL), AWS (RDS), Azure

### Negative

❌ **Learning Curve**: Developers need SQL and relational modeling knowledge
❌ **Schema Rigidity**: Schema changes require migrations (mitigated by Alembic)
❌ **Scaling Complexity**: Vertical scaling easier than horizontal (acceptable for Phase 1-4)
❌ **Resource Usage**: More resource-intensive than some NoSQL alternatives

### Neutral

⚖️ **Operational Overhead**: Requires monitoring, backups, and maintenance
⚖️ **Migration Strategy**: Need careful planning for schema evolution

## Alternatives Considered

### MongoDB (NoSQL Document Store)
- ✅ Flexible schema
- ✅ Horizontal scaling
- ❌ No ACID transactions (before v4.0)
- ❌ Weaker data integrity guarantees
- ❌ Not ideal for relational healthcare data
- **Rejected**: Healthcare data is inherently relational

### MySQL
- ✅ ACID compliant
- ✅ Wide adoption
- ❌ Less feature-rich than PostgreSQL
- ❌ Inferior JSON support
- ❌ Weaker async driver support in Python
- **Rejected**: PostgreSQL offers better features for our use case

### SQLite
- ✅ Zero configuration
- ✅ Embedded database
- ❌ Not suitable for concurrent writes
- ❌ No built-in replication
- ❌ Limited scalability
- **Rejected**: Too limited for production healthcare system

## Implementation

### Technology Stack
- **Database**: PostgreSQL 15+
- **Python Driver**: asyncpg
- **ORM**: SQLAlchemy 2.0 (async mode)
- **Migrations**: Alembic
- **Connection Pooling**: SQLAlchemy engine pooling

### Schema Strategy
- Normalize data to 3rd normal form
- Use UUID for primary keys (security, distributed systems)
- Timestamp all records (created_at, updated_at)
- Soft deletes where appropriate (audit trail)

### Example Configuration
```python
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/triage_db"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
)
```

## Review Date

This decision should be reviewed:
- **Phase 5 (v0.5.0-scale)**: When implementing caching and performance optimization
- **Phase 6 (v0.6.0-production)**: Before production deployment
- **Annually**: As system scales and requirements evolve

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [AsyncPG Documentation](https://magicstack.github.io/asyncpg/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

## Notes

- Redis will be added in Phase 5 for caching (not a replacement for PostgreSQL)
- Consider read replicas in Phase 6 for scaling reads
- Backup strategy critical for production (documented in deployment/docker.md)
