# Drum Dungeon — Docker: Start-to-Finish Summary

This document summarizes the full Docker workflow for the Drum Dungeon app: from the Dockerfile and image build through running the app with MariaDB and testing, so you can run the same setup on any machine (e.g. another VM).

---

## 1. Goal

- **Run the app in a container** so it behaves the same everywhere.
- **Run app + MariaDB together** with one command (Docker Compose).
- **No secrets in the image** — everything from environment and volumes.
- **Portable** — on a new VM: clone repo, set `.env`, run Compose, create admin, done.

---

## 2. Prerequisites

- **Docker** installed (and **Docker Compose** — often available as `docker compose`, not `docker-compose`).
- **Repo** on the machine (e.g. `~/Desktop/drum-dungeon-devops`).
- **Terminal** at the **repo root** (the folder that contains `app/`, `docker/`, and `docker-compose.yml`).

On Ubuntu you may need `sudo` for Docker, or add your user to the `docker` group.

---

## 3. The Dockerfile (`docker/Dockerfile`)

The Dockerfile is the recipe for building the **app image**. It does not include the database.

| Step | Instruction | Purpose |
|------|-------------|---------|
| Base | `FROM python:3.11-slim` | Same Python version as the app; small image. |
| Working dir | `WORKDIR /app` | All later paths are under `/app`. |
| Dependencies | `COPY app/requirements.txt .` then `RUN pip install -r requirements.txt` | Install deps in a separate layer so rebuilds are fast when only code changes. |
| App code | `COPY app/ ./app/` | Puts the FastAPI app at `/app/app/`. |
| Migrations | `COPY alembic/`, `COPY alembic.ini` | So you can run Alembic inside the container. |
| Port | `EXPOSE 8000` | Documents that the app listens on 8000. |
| Start | `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]` | One command to start the app; `0.0.0.0` so it is reachable from outside the container. |

**Important:** No secrets or host-specific paths in the Dockerfile. Configuration comes from environment variables at **runtime**.

---

## 4. `.dockerignore`

This file lives at the **repo root** and tells Docker which files **not** to send to the build (and thus not to put in the image).

We exclude:

- `.git`, `.env`, `practice_data/` — no secrets or local data in the image.
- `__pycache__/`, `.venv/`, `*.pyc` — not needed in the image.
- `docs/`, `*.md` (except README if desired), tests — keeps the image smaller.

Result: faster builds and a smaller, safer image.

---

## 5. Building the Image (app only)

From the **repo root**:

```bash
docker build -f docker/Dockerfile -t drum-dungeon .
```

- `-f docker/Dockerfile` — use this Dockerfile.
- `-t drum-dungeon` — tag the image as `drum-dungeon`.
- `.` — build context is the current directory (respects `.dockerignore`).

After this you have an image named `drum-dungeon` that can run the app. It does **not** start a database.

---

## 6. Testing the Image Without a Database

To confirm the image runs and the health endpoint works **before** adding a DB:

1. Create a directory for practice data (e.g. on the host):
   ```bash
   mkdir -p practice_data
   ```

2. Run the container with the **required** env vars (no `DATABASE_URL`):
   ```bash
   docker run --rm -p 8000:8000 \
     -e SESSION_SECRET_KEY="test-secret-key-for-docker-only-min-32-chars" \
     -e PRACTICE_DATA_DIR=/app/practice_data \
     -v "$(pwd)/practice_data:/app/practice_data" \
     drum-dungeon
   ```

3. In another terminal or in the browser:
   ```bash
   curl -s http://localhost:8000/health
   ```
   Expected (no DB): `{"status":"degraded","database":"not_configured"}` with HTTP 200.

4. Stop the container with Ctrl+C in the terminal where it is running. `--rm` removes the container.

This confirms: image builds, app starts, health endpoint works, and the app can run in “JSON-only” mode when no database is configured.

---

## 7. Docker Compose: App + Database

Compose runs **two services** from one file: the app and MariaDB.

### 7.1 `docker-compose.yml` (repo root)

- **`db` service**
  - Image: `mariadb:11`.
  - Env: `MYSQL_ROOT_PASSWORD` from `.env`, `MYSQL_DATABASE=drum_dungeon`.
  - Volume: `db_data` for persistent DB files.
  - Healthcheck: MariaDB’s `healthcheck.sh` so Compose knows when the DB is ready.

- **`app` service**
  - Build: from `docker/Dockerfile` (context: repo root).
  - Ports: `8000:8000`.
  - Env: `DATABASE_URL` (points to `db:3306`), `SESSION_SECRET_KEY`, `PRACTICE_DATA_DIR=/app/practice_data`, etc.
  - Volume: `practice_data` at `/app/practice_data`.
  - Depends on `db` with `condition: service_healthy` so the app starts only after the DB is ready.
  - Healthcheck: Python one-liner that requests `http://localhost:8000/health`.

- **Volumes**
  - `db_data`: MariaDB data.
  - `practice_data`: app data (e.g. `users.json`, student data).

So: one file defines how the image is built, how the app connects to the DB, and how data is persisted.

### 7.2 Command: `docker compose` vs `docker-compose`

On many systems the plugin is used:

- **Correct:** `docker compose` (space).
- **Legacy:** `docker-compose` (hyphen).

If you get “command not found”, try `docker compose`.

---

## 8. One-Time Setup and Running with Compose

Do this from the **repo root**.

1. **Create `.env` from the template**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and set**
   - `DB_ROOT_PASSWORD` — strong password for MariaDB root (used in `DATABASE_URL`).
   - `SESSION_SECRET_KEY` — required by the app (e.g. generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`).

3. **Build and start**
   ```bash
   docker compose up -d --build
   ```
   - Pulls MariaDB image and builds the app image from `docker/Dockerfile`.
   - Starts `db`, waits for it to be healthy, then starts `app`.
   - Both run in the background (`-d`).

4. **Create the initial admin user** (fresh DB has no users)
   ```bash
   docker compose exec app python -m app.scripts.create_initial_admin --password "YourSecurePassword"
   ```
   Use a real password. Without `--password`, the script may fail in non-interactive environments (e.g. no TTY).

5. **Check health**
   ```bash
   curl -s http://localhost:8000/health
   ```
   Expected: `{"status":"healthy","database":"connected"}`.

6. **Use the app**
   - Login: http://localhost:8000/login (admin + password you set).
   - Admin and student routes work as normal.

---

## 9. Testing That Everything Works

- **Containers:** `docker compose ps` — both services up (db can show “healthy”).
- **Health:** `curl -s http://localhost:8000/health` → `"status":"healthy"`, `"database":"connected"`.
- **Logs:** `docker compose logs app` and `docker compose logs db`.
- **Login:** Admin and test student accounts (create students via admin if needed).

Stopping: `docker compose down`. Add `-v` only if you want to delete the volumes (DB and practice data).

---

## 10. Running on Another VM

The same setup runs on any machine that has Docker and the repo.

1. Install Docker (and Docker Compose plugin if needed).
2. Clone the repo and `cd` into it.
3. `cp .env.example .env` and set `DB_ROOT_PASSWORD` and `SESSION_SECRET_KEY`.
4. Run: `docker compose up -d --build`.
5. Create the initial admin:  
   `docker compose exec app python -m app.scripts.create_initial_admin --password "YourSecurePassword"`
6. Verify: `curl -s http://localhost:8000/health` and log in in the browser.

No need to build the image elsewhere: the **`docker-compose.yml` and Dockerfile** define how the image is built and how the app connects to the DB, so it “builds properly” on that VM.

---

## 11. Common Issues and Fixes

| Issue | Cause | Fix |
|-------|--------|-----|
| `docker-compose: command not found` | Compose is the plugin | Use `docker compose` (space). |
| Port 8000 already in use | Another container or process | Stop it: `docker stop <container>` or free port 8000, then `docker compose up -d --build`. |
| Cannot log in (no users) | Fresh DB has empty `users` table | Run `docker compose exec app python -m app.scripts.create_initial_admin --password "YourPassword"`. |
| `No module named app.scripts.create_initial_admin` | Script added after last build | Rebuild: `docker compose up -d --build`. |
| Script fails with no clear error / getpass | No TTY in `docker exec` | Use `--password "YourPassword"` in the create_initial_admin command. |
| Permission denied (Docker socket) | User not in `docker` group | Run with `sudo` or: `sudo usermod -aG docker $USER`, then log out and back in. |

---

## 12. Summary Checklist

- [ ] **Dockerfile** in `docker/`: base image, deps, app code, Alembic, one CMD with `0.0.0.0`.
- [ ] **`.dockerignore`** at repo root: no `.env`, no `practice_data/`, no unnecessary files.
- [ ] **Build:** `docker build -f docker/Dockerfile -t drum-dungeon .` from repo root.
- [ ] **Test without DB:** run container with `SESSION_SECRET_KEY` and `PRACTICE_DATA_DIR`, volume for practice_data; check `/health` (degraded).
- [ ] **Compose:** `docker-compose.yml` with `db` (MariaDB + healthcheck) and `app` (build from Dockerfile, env, volumes, depends_on db, healthcheck).
- [ ] **Run:** `cp .env.example .env`, set secrets, `docker compose up -d --build`.
- [ ] **Initial admin:** `docker compose exec app python -m app.scripts.create_initial_admin --password "YourPassword"`.
- [ ] **Verify:** `/health` returns healthy + database connected; log in and test admin and student routes.
- [ ] **Other VM:** clone repo, `.env`, `docker compose up -d --build`, create admin, verify.

This is the full process from “only code and a plan” to “app + DB running in Docker and usable on any VM” for educational reference.
