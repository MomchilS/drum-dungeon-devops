# TODO: Drum Dungeon DevOps Project

## ✅ Phase 1 — Codebase Cleanup & Stabilization (COMPLETE)

### Phase 1.1: Remove dead & legacy code
- [x] Move legacy scripts to app/scripts/_legacy/
- [x] Remove unused imports
- [x] Ensure no subprocess calls

### Phase 1.2: Centralize configuration
- [x] Create app/config.py with PRACTICE_DATA_DIR, ENV
- [x] Update imports to use config.py

### Phase 1.3: Finalize stats schema
- [x] Review and ensure consistent initial stats creation

---

## ✅ Phase 2 — Move from JSON → MariaDB (COMPLETE)

### Phase 2.1: Database Design
- [x] Clean 1:1 mapping from JSON to DB tables
- [x] Tables: users, students, xp, attendance, streaks, history_events

### Phase 2.2: Migration Strategy (Dual-Write)
- [x] Dual-write system implemented
- [x] Reads from JSON files (with DB fallback)
- [x] Writes sync to both JSON and MariaDB
- [x] Safe & reversible

### Phase 2.3: Database Implementation
- [x] Database models extracted to app/models.py
- [x] Database connection with pooling
- [x] Alembic migrations set up
- [x] Health check endpoint (/health)

### Phase 2.4: Secrets Management
- [x] Environment variables for all secrets
- [x] .env.example template created
- [x] No hardcoded credentials

---

## ✅ Phase 3 — Dockerization (COMPLETE)

### 3.1–3.6
- [x] Create Dockerfile in `docker/`
- [x] Create .dockerignore
- [x] Run app container only (with host or no DB)
- [x] Add docker-compose.yml (app + db, env, volumes)
- [x] Add healthchecks in Compose
- [x] Document and test full flow (docs/docker-run.md, docs/docker-summary.md)
- [x] Create initial admin script for fresh DB

**Next:** Phase 4 — Infrastructure (Terraform + Ansible)