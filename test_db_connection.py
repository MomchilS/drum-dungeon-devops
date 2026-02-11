#!/usr/bin/env python3
"""
Test database connection directly.
"""

import os
import sys
from pathlib import Path

# Load environment variables FIRST
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print("[OK] Loaded .env file")
except ImportError:
    pass

# Verify DATABASE_URL is set
DATABASE_URL = os.getenv("DATABASE_URL")
print(f"DATABASE_URL: {DATABASE_URL}")

if not DATABASE_URL:
    print("[ERROR] DATABASE_URL not set!")
    sys.exit(1)

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

# Try to load database module
print("\n[1] Testing database module load...")
try:
    from app.database import _load_database, DB_AVAILABLE, SessionLocal
    
    print(f"Before _load_database(): DB_AVAILABLE = {DB_AVAILABLE}")
    
    # Force load
    _load_database()
    
    print(f"After _load_database(): DB_AVAILABLE = {DB_AVAILABLE}")
    
    if DB_AVAILABLE:
        print("[OK] Database module loaded successfully!")
        
        if SessionLocal:
            print("[OK] SessionLocal is available")
            
            # Test connection
            db = SessionLocal()
            try:
                from sqlalchemy import text
                result = db.execute(text("SELECT 1"))
                print("[OK] Can execute queries!")
                db.close()
            except Exception as e:
                print(f"[ERROR] Query failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("[ERROR] SessionLocal is None")
    else:
        print("[ERROR] DB_AVAILABLE is still False after _load_database()")
        print("       Trying to manually test connection...")
        
        # Try to manually create engine to see the error
        try:
            from sqlalchemy import create_engine
            test_engine = create_engine(DATABASE_URL)
            with test_engine.connect() as conn:
                from sqlalchemy import text
                result = conn.execute(text("SELECT 1"))
                print("[OK] Manual connection test succeeded!")
                print("       The issue is in the database module's _load_database() function")
        except Exception as e:
            print(f"[ERROR] Manual connection also failed: {e}")
            import traceback
            traceback.print_exc()
        
except Exception as e:
    print(f"[ERROR] Failed to load database module: {e}")
    import traceback
    traceback.print_exc()
