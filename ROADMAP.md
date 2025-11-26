# Project Roadmap: Patient Triage & Management System

## Project Vision
This backend repository demonstrates the evolution of a production-grade healthcare system. It solves the problem of **symptom standardization** by integrating the **NLM Medical Conditions API** to validate patient inputs against official ICD-10 codes, powering an automated triage and recommendation engine.

## How to Navigate This Repository
Unlike typical tutorials, this project uses **Annotated Tags** to demonstrate progressive growth. Each tag represents a complete, working milestone.
* **Do not look for feature branches.**
* **Checkout specific tags** to view the codebase at that specific stage of maturity.
* **Read the Release Notes** for each tag to understand the architectural decisions made at that step.

---

## The 12-Week Progression

### Phase 1: Foundation & Infrastructure (Weeks 1-2)
**Goal:** Establish the Clean Architecture skeleton, database connectivity, and basic user identity.
* **Features:**
    * FastAPI application structure (Domain/Application/Infra/Presentation).
    * PostgreSQL + SQLAlchemy 2.0 (Async) setup.
    * User Registration & JWT Authentication (Stateless).
    * Docker Compose environment.
* **Architectural Focus:** Separation of concerns, Dependency Injection setup (Dishka/FastAPI Depends).
* **Tag:** `v0.1.0-mvp`

### Phase 2: The Triage & Recommendation Engine (Weeks 3-4)
**Goal:** Implement the core differentiator—integrating external clinical data to drive business logic.
* **Features:**
    * **NLM API Integration:** Adapter implementation to search/validate symptoms via `clinicaltables.nlm.nih.gov`.
    * **Triage Domain Service:** Logic to map ICD-10 codes to urgency levels (Low/Medium/High).
    * **Specialty Recommendation:** Auto-suggesting "Cardiology" vs "General Practice" based on standardized symptoms.
    * **Provider Scheduling:** Basic appointment slots linked to specific specialties.
* **Architectural Focus:** External System Adapters (Ports & Adapters), Strategy Pattern for Triage Logic, Handling 3rd party API failures.
* **Tag:** `v0.2.0-triage-core`

### Phase 3: Security & HIPAA Compliance (Weeks 5-6)
**Goal:** Harden the application with healthcare-specific security controls.
* **Features:**
    * **RBAC (Role-Based Access Control):** Granular permissions for Admin, Provider, Nurse, and Patient.
    * **Audit Logging:** Immutable logs capturing Who, What, When, Where (IP), and Why for every record access.
    * **Security Headers & Sanitization:** Pydantic validators for XSS prevention and input sanitization.
    * **Rate Limiting:** Protecting auth endpoints against brute force.
* **Architectural Focus:** Middleware implementation, AOP (Aspect Oriented Programming) for logging, Security-by-Design.
* **Tag:** `v0.3.0-security`

### Phase 4: Clinical Data Management (Weeks 7-8)
**Goal:** Manage complex domain entities and maintain data integrity.
* **Features:**
    * **Medical Records:** Linking Appointments to Patient History and ICD-10 codes.
    * **Prescriptions:** Entity relationships for medications.
    * **Vital Signs Validation:** Domain logic ensuring physiological ranges (e.g., rejecting a HR of 300 bpm).
    * **Conflict Detection:** Advanced SQL locking to prevent double-booking.
* **Architectural Focus:** Database constraints, Complex Entity Relationships, Transaction Management (Unit of Work).
* **Tag:** `v0.4.0-clinical`

### Phase 5: Scale & Performance (Weeks 9-10)
**Goal:** Optimize the system for high-read throughput and larger datasets.
* **Features:**
    * **Redis Caching:** Caching NLM API responses (ICD codes rarely change) and Provider Availability.
    * **Cursor-Based Pagination:** Efficiently serving large lists of audit logs and appointments.
    * **Database Indexing:** Optimizing query plans for common search patterns.
    * **Background Tasks:** Sending appointment reminders via Celery/Arq.
* **Architectural Focus:** Caching Strategies (Cache-Aside), Query Optimization, Asynchronous Processing.
* **Tag:** `v0.5.0-scale`

### Phase 6: Observability & Production Readiness (Weeks 11-12)
**Goal:** Make the system observable and ready for "Day 2" operations.
* **Features:**
    * **OpenTelemetry:** Distributed tracing to visualize the flow from API Request $\rightarrow$ DB $\rightarrow$ NLM API.
    * **Structured Logging:** JSON logs for easy parsing by aggregation tools.
    * **Health Checks:** Deep endpoints checking DB and Redis connectivity.
    * **Prometheus Metrics:** Exposing request latency and error rates.
* **Architectural Focus:** DevOps, Monitoring, Debuggability.
* **Tag:** `v0.6.0-production`

---

## Architecture Decisions (ADRs)
Major technical decisions are documented in `/docs/decisions`:
* `ADR-001`: Use PostgreSQL for relational data integrity.
* `ADR-002`: Adopt Dishka for Framework-Agnostic Dependency Injection.
* `ADR-005`: External Symptom Validation via NLM API.

## Tech Stack
* **Language:** Python 3.11+
* **Framework:** FastAPI
* **Database:** PostgreSQL (AsyncPg), Redis
* **ORM:** SQLAlchemy 2.0
* **Validation:** Pydantic V2
* **Testing:** Pytest (Unit, Integration, E2E)
* **Observability:** OpenTelemetry, Prometheus