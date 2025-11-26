# Dockerfile for Streamlit Frontend
# Expects to be built from root context with pyproject.toml

FROM python:3.11-slim

# Install PDM
RUN pip install --no-cache-dir pdm

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

WORKDIR /project

# Copy root dependency files
COPY --chown=appuser:appuser pyproject.toml ./

# Generate requirements and install with pip
RUN pdm lock && pdm export --prod --without-hashes -f requirements > requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend application code
WORKDIR /app
COPY --chown=appuser:appuser frontend/ ./

# Switch to non-root user
USER appuser

# Expose Streamlit port
EXPOSE 8501

# Set Python path
ENV PYTHONPATH=/app

# Streamlit configuration
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true

# Run Streamlit
CMD ["python", "-m", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
