# Multi-stage build for FastAPI backend
# Expects to be built from root context with pyproject.toml

FROM python:3.11-slim AS builder

# Install PDM
RUN pip install --no-cache-dir pdm

# Set working directory
WORKDIR /project

# Copy root dependency files
COPY pyproject.toml ./

# Generate requirements and install with pip
RUN pdm lock && pdm export --prod --without-hashes -f requirements > requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy backend application code
COPY --chown=appuser:appuser backend/src/ /app/
COPY --chown=appuser:appuser backend/alembic.ini /app/
COPY --chown=appuser:appuser backend/alembic/ /app/alembic/

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Set Python path
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/public/v1/health || exit 1

# Run uvicorn
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
