# Running Drum Dungeon with Docker and Docker Compose

This doc covers: (1) connecting the app to the DB with Compose, (2) testing the setup, and (3) running on another VM.

---

## 1. Connect app to the database (Docker Compose)

We use **one Compose file** that runs both the app and MariaDB. The app gets `DATABASE_URL` pointing at the `db` service so it connects automatically.

### Prerequisites

- Docker and Docker Compose installed
- From the **repo root** (where `docker-compose.yml` lives)

### One-time setup

1. **Create `.env` from the template**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and set:**
   - `DB_ROOT_PASSWORD` — strong password for MariaDB root (e.g. used by Compose for `DATABASE_URL`)
   - `SESSION_SECRET_KEY` — required by the app (e.g. generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
   - Optionally `PRACTICE_DATA_DIR` — Compose defaults to `/app/practice_data` in the container; you usually don’t need to change it.

3. **Build and start**
   ```bash
   docker-compose up -d --build
   ```
   - `--build` builds the app image from `docker/Dockerfile`.
   - `-d` runs in the background.
   - Compose starts `db` first; when the DB healthcheck passes, it starts `app` with `DATABASE_URL=...@db:3306/drum_dungeon`.

4. **Apply database schema (first time only)**
   The MariaDB image creates the `drum_dungeon` database. You still need to run migrations:
   ```bash
   docker-compose exec app alembic upgrade head
   ```
   (If Alembic has no migrations yet, create them first from the host and rebuild, or run `create_db` logic; the app also creates tables on first connect via `Base.metadata.create_all` in `database.py`, so the app may work without Alembic for a minimal test.)

5. **Create the initial admin user** (fresh DB has no users, so you cannot log in until you create one).  
   If you added the script after building the image, rebuild first: `docker compose up -d --build`
   ```bash
   docker compose exec app python -m app.scripts.create_initial_admin
   ```
   You will be prompted for a password, or pass it explicitly:
   ```bash
   docker compose exec app python -m app.scripts.create_initial_admin --password "YourSecurePassword"
   ```
   Or set `INITIAL_ADMIN_PASSWORD` in the environment.

6. **Check health**
   ```bash
   curl -s http://localhost:8000/health
   ```
   With DB connected you should see something like: `{"status":"healthy","database":"connected"}`.

---

## 2. Testing that the image works (with DB)

1. **Start stack:** `docker-compose up -d --build`
2. **Wait for healthy:** `docker-compose ps` — both `app` and `db` should show “healthy” (or “running” until healthchecks pass).
3. **Healthcheck:** `curl -s http://localhost:8000/health` → expect `"status":"healthy"` and `"database":"connected"` once DB is up and migrations/app have run.
4. **Open in browser:** http://localhost:8000 and http://localhost:8000/health.
5. **Logs:** `docker-compose logs -f app` or `docker-compose logs -f db`.
6. **Stop:** `docker-compose down`. Data in named volumes (`db_data`, `practice_data`) is kept. Use `docker-compose down -v` to remove volumes.

So: **build with Compose → start app + DB → run migrations once → hit /health and the app** to confirm the image works with the DB.

---

## 3. Running on another VM (so the YML builds and runs there)

The goal is: on a **new VM**, clone the repo and run the same `docker-compose.yml` so the app and DB start without hand‑holding.

### On the new VM

1. **Install Docker and Docker Compose** (if not already installed).
2. **Clone the repo**
   ```bash
   git clone <your-repo-url> drum-dungeon-devops
   cd drum-dungeon-devops
   ```
3. **Create `.env`**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set **real** values for:
   - `DB_ROOT_PASSWORD`
   - `SESSION_SECRET_KEY`
4. **Build and start**
   ```bash
   docker-compose up -d --build
   ```
   Compose will:
   - Build the app image from `docker/Dockerfile` (context: repo root).
   - Pull the MariaDB image.
   - Start `db`, wait for it to be healthy, then start `app` with the correct `DATABASE_URL`.
5. **First-time DB setup** (if using Alembic): `docker compose exec app alembic upgrade head`
6. **Create initial admin** (fresh DB has no users): `docker compose exec app python -m app.scripts.create_initial_admin`
7. **Verify:** `curl -s http://localhost:8000/health`

As long as the VM has Docker and Compose and can clone the repo, the **same `docker-compose.yml` and Dockerfile** ensure the image is built and run consistently there. No need to build the image elsewhere and copy it, unless you introduce a registry later.

---

## Summary

| Step | What you do |
|------|----------------|
| Connect app to DB | Use `docker-compose.yml` (app + db, env, volumes, healthchecks). |
| Test image + DB | `docker compose up -d --build` → create initial admin → `curl localhost:8000/health`. |
| Another VM | Clone repo → `cp .env.example .env` → set secrets → `docker compose up -d --build` → create initial admin → verify `/health`. |

The YML file is the contract: it defines how the image is built (`build: context: . dockerfile: docker/Dockerfile`) and how the app connects to the DB (`DATABASE_URL` and `depends_on: db`), so it will build and run the same way on any VM that has Docker and the repo.
