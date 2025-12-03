#!/bin/bash
#
# Patient Triage System - First Time Setup Script
#
# This script automates the complete setup process:
# 1. Starts PostgreSQL via Docker
# 2. Waits for PostgreSQL to be ready
# 3. Creates the database
# 4. Runs migrations
#
# Usage:
#   chmod +x scripts/setup.sh
#   ./scripts/setup.sh
#
# Or with PDM:
#   pdm run setup
#

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration (can be overridden by environment variables)
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-triage_db}"
MAX_RETRIES=30
RETRY_INTERVAL=2

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Patient Triage System - First Time Setup              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Check if Docker is running
echo -e "${YELLOW}[1/5]${NC} Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"

# Step 2: Start PostgreSQL container
echo -e "${YELLOW}[2/5]${NC} Starting PostgreSQL container..."
docker-compose up -d postgres

# Step 3: Wait for PostgreSQL to be ready
echo -e "${YELLOW}[3/5]${NC} Waiting for PostgreSQL to be ready..."
RETRIES=0
until docker exec triage-postgres pg_isready -U "$POSTGRES_USER" > /dev/null 2>&1; do
    RETRIES=$((RETRIES + 1))
    if [ $RETRIES -ge $MAX_RETRIES ]; then
        echo -e "${RED}✗ PostgreSQL did not become ready in time${NC}"
        exit 1
    fi
    echo -n "."
    sleep $RETRY_INTERVAL
done
echo ""
echo -e "${GREEN}✓ PostgreSQL is ready${NC}"

# Step 4: Create database if it doesn't exist
echo -e "${YELLOW}[4/5]${NC} Creating database '${POSTGRES_DB}'..."
docker exec triage-postgres psql -U "$POSTGRES_USER" -tc \
    "SELECT 1 FROM pg_database WHERE datname = '$POSTGRES_DB'" | grep -q 1 \
    && echo -e "${GREEN}✓ Database '$POSTGRES_DB' already exists${NC}" \
    || {
        docker exec triage-postgres psql -U "$POSTGRES_USER" -c "CREATE DATABASE $POSTGRES_DB"
        echo -e "${GREEN}✓ Database '$POSTGRES_DB' created${NC}"
    }

# Step 5: Run migrations
echo -e "${YELLOW}[5/5]${NC} Running database migrations..."
pdm run migrate
echo -e "${GREEN}✓ Migrations complete${NC}"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    Setup Complete! 🎉                      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Next steps:"
echo -e "  ${BLUE}1.${NC} Start the backend:    ${YELLOW}pdm run dev-backend${NC}"
echo -e "  ${BLUE}2.${NC} Start the frontend:   ${YELLOW}pdm run dev-frontend${NC}"
echo -e "  ${BLUE}3.${NC} Open API docs:        ${YELLOW}http://localhost:8000/docs${NC}"
echo ""
echo -e "Or start everything with Docker:"
echo -e "  ${YELLOW}pdm run docker-up${NC}"
echo ""
