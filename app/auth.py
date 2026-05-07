from passlib.context import CryptContext

# Import database components conditionally
try:
    import app.database as database
    from app.models import User
except ImportError:
    # Handle case where database module fails to import
    database = None
    User = None

# ------------------------------------------------------------------
# Password hashing configuration
# ------------------------------------------------------------------

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

# ------------------------------------------------------------------
# User loading helpers
# ------------------------------------------------------------------

def _require_db_session():
    if not database or not database.DB_AVAILABLE or database.SessionLocal is None:
        raise RuntimeError("Database is required for runtime auth operations")
    return database.SessionLocal()


def load_users():
    db = _require_db_session()
    try:
        users_db = db.query(User).all()
        return {
            user.username: {
                "password": user.password,
                "role": user.role,
                "force_change": user.force_change,
            }
            for user in users_db
        }
    finally:
        db.close()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ------------------------------------------------------------------
# User management
# ------------------------------------------------------------------

def update_password(username: str, new_password: str):
    db = _require_db_session()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise KeyError(f"User '{username}' not found")
        user.password = hash_password(new_password)
        user.force_change = False
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def delete_user(username: str):
    db = _require_db_session()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user:
            db.delete(user)
            db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def add_user(username: str, password: str, role: str, force_change: bool):
    hashed_password = hash_password(password)

    db = _require_db_session()
    try:
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            existing_user.password = hashed_password
            existing_user.role = role
            existing_user.force_change = force_change
        else:
            user = User(
                username=username,
                password=hashed_password,
                role=role,
                force_change=force_change
            )
            db.add(user)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
