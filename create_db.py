#!/usr/bin/env python3
"""Create PostgreSQL database if it does not exist."""

import os
import psycopg2
from psycopg2 import sql
from urllib.parse import urlparse

# Get database connection details from environment
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable is not set.")
    print("Example: postgresql+psycopg2://user:password@host/database")
    exit(1)

# Parse DATABASE_URL
# Format: postgresql+psycopg2://user:password@host/database
try:
    parsed = urlparse(DATABASE_URL.replace("postgresql+psycopg2://", "postgresql://"))
    user = parsed.username
    password = parsed.password
    host = parsed.hostname or "localhost"
    port = parsed.port or 5432
    database = parsed.path.lstrip("/") or "drum_dungeon"
except Exception as e:
    print(f"Error parsing DATABASE_URL: {e}")
    exit(1)

try:
    connection = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname="postgres"
    )
    connection.autocommit = True
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database,))
        exists = cursor.fetchone()
        if not exists:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database)))
            print(f"Database '{database}' created.")
        else:
            print(f"Database '{database}' already exists.")
except Exception as e:
    print(f"Error creating database: {e}")
    exit(1)
finally:
    if 'connection' in locals():
        connection.close()
