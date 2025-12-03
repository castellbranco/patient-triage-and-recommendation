#!/usr/bin/env python3
"""
Database Initialization Script
"""

import asyncio
import sys

import asyncpg


async def init_database(
    host: str = "localhost",
    port: int = 5432,
    user: str = "postgres",
    password: str = "postgres",
    database: str = "triage_db",
) -> None:
    """
    Create the database if it doesn't exist.
    """
    # Connect to default postgres database
    sys_conn = await asyncpg.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database="postgres",
    )
    
    try:
        exists = await sys_conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            database,
        )
        
        if exists:
            print(f"✓ Database '{database}' already exists")
        else:
            # Create the database
            await sys_conn.execute(f'CREATE DATABASE "{database}"')
            print(f"✓ Database '{database}' created successfully")
            
    finally:
        await sys_conn.close()


def main() -> None:
    """Main entry point."""
    import os
    
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    database = os.getenv("POSTGRES_DB", "triage_db")
    
    print(f"Initializing database at {host}:{port}...")
    
    try:
        asyncio.run(init_database(host, port, user, password, database))
        print("✓ Database initialization complete!")
        print(f"\nNext step: Run 'pdm run migrate' to create tables")
    except asyncpg.exceptions.InvalidCatalogNameError:
        print(f"✗ Could not connect to PostgreSQL at {host}:{port}")
        print("  Make sure PostgreSQL is running (docker-compose up -d)")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
