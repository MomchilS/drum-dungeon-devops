#!/usr/bin/env python3
"""
Database diagnostic script - checks MariaDB connection and user data.
"""

import os
import sys
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print("[OK] Loaded environment variables from .env")
except ImportError:
    print("[WARN] python-dotenv not installed")

# Check environment variables
print("\n" + "="*60)
print("DATABASE DIAGNOSTIC CHECK")
print("="*60)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("[ERROR] DATABASE_URL not set in environment")
    sys.exit(1)

print(f"DATABASE_URL: {DATABASE_URL}")

# Parse database URL
from urllib.parse import urlparse
parsed = urlparse(DATABASE_URL.replace("mysql+pymysql://", "mysql://"))
db_host = parsed.hostname or "localhost"
db_user = parsed.username or "root"
db_password = parsed.password
db_name = parsed.path.lstrip("/") if parsed.path else "drum_dungeon"

print(f"\nDatabase Connection Details:")
print(f"  Host: {db_host}")
print(f"  User: {db_user}")
print(f"  Database: {db_name}")
print(f"  Password: {'[OK] Set' if db_password else '[ERROR] Not set'}")

# Test 1: Check if we can connect to MariaDB
print("\n" + "-"*60)
print("TEST 1: MariaDB Connection")
print("-"*60)

try:
    import pymysql
    connection = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    print("[OK] Successfully connected to MariaDB")
    connection.close()
except pymysql.Error as e:
    print(f"[ERROR] Failed to connect to MariaDB: {e}")
    print("\nTrying to connect without database (to create it)...")
    try:
        connection = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password
        )
        print("[OK] Can connect to MariaDB server")
        
        # Try to create database
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            connection.commit()
            print(f"[OK] Database '{db_name}' created or already exists")
        
        connection.close()
        
        # Try connecting again
        connection = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        print("[OK] Successfully connected to database")
        connection.close()
    except Exception as e2:
        print(f"❌ Failed: {e2}")
        sys.exit(1)
except ImportError:
    print("[ERROR] pymysql not installed. Install with: pip install pymysql")
    sys.exit(1)

# Test 2: Check if tables exist
print("\n" + "-"*60)
print("TEST 2: Database Tables")
print("-"*60)

try:
    import pymysql
    connection = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if tables:
            print(f"[OK] Found {len(tables)} table(s):")
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("[WARN] No tables found. Database might need initialization.")
            print("   Run: python create_db.py")
            print("   Or the app will create tables on first run")
    
    connection.close()
except Exception as e:
    print(f"❌ Error checking tables: {e}")

# Test 3: Check users table and data
print("\n" + "-"*60)
print("TEST 3: Users in Database")
print("-"*60)

try:
    import pymysql
    connection = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    
    with connection.cursor() as cursor:
        # Check if users table exists
        cursor.execute("SHOW TABLES LIKE 'users'")
        if cursor.fetchone():
            cursor.execute("SELECT username, role, force_change FROM users")
            users = cursor.fetchall()
            
            if users:
                print(f"[OK] Found {len(users)} user(s) in database:")
                for user in users:
                    username, role, force_change = user
                    print(f"   - {username} (role: {role}, force_change: {force_change})")
            else:
                print("[WARN] No users found in database")
                print("   Users might be stored in JSON files only")
        else:
            print("[WARN] 'users' table does not exist")
            print("   The app will create it on first run")
    
    connection.close()
except Exception as e:
    print(f"❌ Error checking users: {e}")

# Test 4: Check JSON users file
print("\n" + "-"*60)
print("TEST 4: Users in JSON File")
print("-"*60)

try:
    from app.config import PRACTICE_DATA_DIR
    users_file = PRACTICE_DATA_DIR / "users.json"
    
    if users_file.exists():
        import json
        with open(users_file, 'r') as f:
            users = json.load(f)
        
        if users:
            print(f"✅ Found {len(users)} user(s) in JSON file:")
            for username, user_data in users.items():
                role = user_data.get('role', 'unknown')
                force_change = user_data.get('force_change', False)
                print(f"   - {username} (role: {role}, force_change: {force_change})")
        else:
            print("⚠️  No users in JSON file")
    else:
        print(f"[WARN] users.json not found at: {users_file}")
        print("   This is normal if you're using database-only mode")
except Exception as e:
    print(f"[ERROR] Error checking JSON users: {e}")

# Test 5: Check app database connection
print("\n" + "-"*60)
print("TEST 5: App Database Connection")
print("-"*60)

try:
    # Set up environment for app imports
    sys.path.insert(0, str(Path(__file__).parent))
    
    from app.database import DB_AVAILABLE, SessionLocal, User
    
    if DB_AVAILABLE:
        print("[OK] App database module reports DB_AVAILABLE = True")
        
        if SessionLocal:
            db = SessionLocal()
            try:
                # Try to query users
                users = db.query(User).all()
                print(f"[OK] Can query database. Found {len(users)} user(s) via SQLAlchemy")
                for user in users:
                    print(f"   - {user.username} (role: {user.role}, force_change: {user.force_change})")
            except Exception as e:
                print(f"[WARN] Error querying via SQLAlchemy: {e}")
            finally:
                db.close()
        else:
            print("[WARN] SessionLocal is None")
    else:
        print("[ERROR] App database module reports DB_AVAILABLE = False")
        print("   Check DATABASE_URL environment variable")
        
except Exception as e:
    print(f"❌ Error checking app database: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Check authentication
print("\n" + "-"*60)
print("TEST 6: Authentication Check")
print("-"*60)

try:
    sys.path.insert(0, str(Path(__file__).parent))
    from app.auth import load_users, verify_password
    
    users = load_users()
    
    if users:
        print(f"[OK] Auth module can load {len(users)} user(s):")
        for username in users.keys():
            print(f"   - {username}")
        
        # Test password verification for admin
        if 'admin' in users:
            admin_password_hash = users['admin']['password']
            print(f"\n   Admin password hash: {admin_password_hash[:20]}...")
            print("   (To test login, you need the actual password)")
    else:
        print("[WARN] No users found by auth module")
        
except Exception as e:
    print(f"❌ Error checking authentication: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("DIAGNOSTIC COMPLETE")
print("="*60)
print("\nNext steps:")
print("1. If database doesn't exist, run: python create_db.py")
print("2. If no users exist, create them via admin panel or manually")
print("3. Check that SESSION_SECRET_KEY is set in .env")
print("4. Make sure MariaDB service is running")
