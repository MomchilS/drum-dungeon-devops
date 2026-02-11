# Drum Dungeon – DevOps Project

A DevOps project for a browser-based game using:

- FastAPI
- MariaDB
- Alembic (Database Migrations)

## Current Status

**Phase 2 Complete** - Application is working with:
- ✅ Dual-write database strategy (JSON + MariaDB)
- ✅ Database models and migrations
- ✅ Health check endpoint
- ✅ Environment-based configuration
- ✅ Secrets management via .env

**Ready for Phase 3** - Dockerization

## Project Structure

```
drum-dungeon-devops/
├── app/                    # FastAPI application
│   ├── models.py          # Database models
│   ├── database.py        # Database connection
│   ├── main.py            # FastAPI app
│   └── services/          # Business logic
├── alembic/               # Database migrations
└── docs/                  # Documentation
```

## Quick Start

### Local Development

1. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your values (DATABASE_URL, SESSION_SECRET_KEY, etc.)
   ```

2. **Create database:**
   ```bash
   python create_db.py
   ```

3. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

4. **Start application:**
   ```bash
   cd app
   python -m uvicorn main:app --reload
   ```

5. **Access application:**
   - App: http://localhost:8000
   - Health: http://localhost:8000/health

## Database Testing

- `check_database.py` - Comprehensive database diagnostic
- `test_db_connection.py` - Test database connectivity
- `db_viewer.py` - View database contents
- `create_db.py` - Create database if it doesn't exist

## Security

- All secrets managed via environment variables (.env file)
- No hardcoded credentials in code
- Health check endpoint for monitoring

## Next Steps

Ready to proceed with Phase 3: Dockerization
