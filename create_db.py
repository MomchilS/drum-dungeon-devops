#!/usr/bin/env python3
"""
Script to create the drum_dungeon database if it doesn't exist.
"""

import pymysql

# Database connection details
host = "localhost"
user = "root"
password = "Naruto6767momo"
database = "drum_dungeon"

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
finally:
    if 'connection' in locals():
        connection.close()
