#!/usr/bin/env python3
"""
Script to create the drum_dungeon database if it doesn't exist.
Uses environment variables for credentials.
"""

import os
import pymysql
from urllib.parse import urlparse

# Get database connection details from environment
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable is not set.")
    print("Example: mysql+pymysql://user:password@host/database")
    exit(1)

# Parse DATABASE_URL
# Format: mysql+pymysql://user:password@host/database
try:
    parsed = urlparse(DATABASE_URL.replace("mysql+pymysql://", "mysql://"))
    user = parsed.username
    password = parsed.password
    host = parsed.hostname or "localhost"
    database = parsed.path.lstrip("/") or "drum_dungeon"
except Exception as e:
    print(f"Error parsing DATABASE_URL: {e}")
    exit(1)

try:
    # Connect without specifying database to create it
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password
    )
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        print(f"Database '{database}' created or already exists.")
    connection.commit()
except Exception as e:
    print(f"Error creating database: {e}")
    exit(1)
finally:
    if 'connection' in locals():
        connection.close()
