# Phase 3: Dockerization — Plan & Learning Guide

## Part 1: What Does "Docker Ready" Mean?

**Docker ready** means your application can run inside a **container** without changing its code. A container is an isolated environment: it has its own filesystem, network, and process space. For the app to run there, it must not depend on things that only exist on your laptop (fixed paths, local-only services, hardcoded secrets).

Below are the main traits of a Docker-ready app and how Drum Dungeon already fits them.

---

### 1. Configuration via environment variables

**Idea:** No paths, hostnames, or secrets hardcoded in code. Everything comes from the **environment** (e.g. `PRACTICE_DATA_DIR`, `DATABASE_URL`, `SESSION_SECRET_KEY`).

**Why it matters for Docker:**  
The same image can run locally, in Docker, or in production. You only change env vars; the code stays the same.

**In this app:**
- `app/config.py` uses `os.environ["PRACTICE_DATA_DIR"]` and `os.getenv("ENV", "local")`.
- Database URL comes from `DATABASE_URL`.
- Session secret from `SESSION_SECRET_KEY`.

So the app is **config-driven**, not tied to one machine.

---

### 2. No hard dependency on the host machine

**Idea:** The app does not assume a specific OS, user, or absolute path (e.g. `C:\Users\...` or `/home/...`). It uses paths and settings provided at runtime.

**Why it matters for Docker:**  
Inside the container the filesystem is different. Paths like `C:\Users\momch\...` do not exist there.

**In this app:**  
All paths are derived from `PRACTICE_DATA_DIR`. In Docker you set e.g. `PRACTICE_DATA_DIR=/app/data` and the app works. So the app is **portable**.

---

### 3. State is external or mountable

**Idea:** Important data (DB, uploads, logs) is not “baked into” the app image. It lives in:
- a **database** (e.g. MariaDB) or  
- **volumes** (directories mounted into the container).

**Why it matters for Docker:**  
Containers are ephemeral. If you remove the container, anything only inside it is gone. So the app should expect DB and data dir to be provided from outside.

**In this app:**  
- Data is in MariaDB (separate service) and in files under `PRACTICE_DATA_DIR`.
- In Docker, you will run **two** containers: one for the app, one for MariaDB, and mount a volume for `PRACTICE_DATA_DIR` (and DB data). So the app is **stateless** in the right way.

---

### 4. Single, clear way to start

**Idea:** One command starts the app (e.g. `uvicorn app.main:app`). No manual “run this script, then that, then open this port”.

**Why it matters for Docker:**  
The Dockerfile has one `CMD` (or `ENTRYPOINT`). That command should be “start the app”.

**In this app:**  
You start with: `uvicorn main:app --host 0.0.0.0 --port 8000`. One command. So the app has a **single entry point**.

---

### 5. Dependencies are declared

**Idea:** All dependencies are listed in a file (e.g. `requirements.txt`). No hidden “you also need to install X”.

**Why it matters for Docker:**  
The Dockerfile runs `pip install -r requirements.txt` and gets a **reproducible** environment.

**In this app:**  
`app/requirements.txt` lists FastAPI, uvicorn, sqlalchemy, pymysql, etc. So the app has **declared dependencies**.

---

### 6. Listens on 0.0.0.0 (not only localhost)

**Idea:** The app binds to `0.0.0.0`, so it accepts connections from **outside** the container (e.g. from your host or a load balancer).

**Why it matters for Docker:**  
Inside the container, `localhost` is only the container itself. If the app binds to `127.0.0.1`, nothing from outside can reach it.

**In this app:**  
When you run uvicorn you use `--host 0.0.0.0`, so the app is **network-accessible** from Docker’s perspective.

---

### 7. Health check endpoint

**Idea:** The app exposes an HTTP endpoint (e.g. `/health`) that returns 200 when the app (and optionally DB) is OK.

**Why it matters for Docker:**  
Docker and orchestrators (e.g. Kubernetes) can run a **healthcheck** and restart the container if the app is unhealthy.

**In this app:**  
`/health` checks DB connectivity and returns JSON with status. So the app is **observable** for Docker.

---

### 8. Logs go to stdout/stderr

**Idea:** Application logs are written to **standard output/error**, not only to a file on disk.

**Why it matters for Docker:**  
Docker captures stdout/stderr. So `docker logs <container>` and log drivers work without extra file handling.

**In this app:**  
Using `print()` and Python’s `logging` (default handler to stderr) is enough. So the app is **log-friendly** for containers.

---

## Summary: Why this app is Docker ready

| Criterion                 | In this app                                      |
|--------------------------|--------------------------------------------------|
| Config via env vars      | `PRACTICE_DATA_DIR`, `DATABASE_URL`, `ENV`, etc. |
| No host-specific paths   | All paths from env                               |
| External/mountable state | MariaDB + `PRACTICE_DATA_DIR`                     |
| Single start command     | `uvicorn main:app ...`                           |
| Declared dependencies   | `requirements.txt`                               |
| Binds to 0.0.0.0         | Via uvicorn `--host 0.0.0.0`                     |
| Health endpoint          | `/health`                                        |
| Logs to stdout/stderr    | `print` / `logging`                               |

So: **Docker ready** = the app can run in a container with **only** environment variables and mounted volumes; no code changes needed.

---

## Part 2: Phase 3 plan (step-by-step)

Goal: run the app and MariaDB in Docker, so you learn each piece.

**Prerequisites:** Docker must be installed. On Windows, install [Docker Desktop](https://www.docker.com/products/docker-desktop/); then open a new terminal and run `docker --version` to confirm.

### Step 3.1 — Add a Dockerfile (done)

**What:** A Dockerfile is a recipe to build an **image** (filesystem + app + runtime).

**Created:** `docker/Dockerfile`. Every line is explained in comments in the file.

**Quick reference:**

| Line / block | Purpose |
|--------------|--------|
| `FROM python:3.11-slim` | Base image: Python 3.11 on a minimal OS. |
| `WORKDIR /app` | All later commands run from `/app` in the container. |
| `COPY app/requirements.txt .` | Copy only the dependency list first (for layer caching). |
| `RUN pip install --no-cache-dir -r requirements.txt` | Install dependencies; no pip cache to keep image small. |
| `COPY app/ ./app/` | Copy app code to `/app/app/` so `app` is a Python package. |
| `COPY alembic/ ./alembic/` and `COPY alembic.ini .` | Copy migrations so you can run them in the container. |
| `EXPOSE 8000` | Documents that the app listens on 8000; publishing is done with `docker run -p`. |
| `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]` | Default command: run the app; `0.0.0.0` so it accepts connections from outside the container. |

**Build:** From project root run: `docker build -f docker/Dockerfile -t drum-dungeon .`  
**Learning outcome:** You understand how an image is built and why we use a slim base and a single CMD.

---

### Step 3.2 — Add .dockerignore

**What:** A `.dockerignore` file tells Docker which files **not** to copy into the image (e.g. `.git`, `__pycache__`, `.env`, `practice_data/`).

**You will:**  
Create `.dockerignore` and list patterns to exclude.

**Learning outcome:** Smaller, faster builds and no secrets or local data in the image.

---

### Step 3.3 — Run the app container only (no DB in Docker yet)

**What:** Build the image and run **one** container with the app. Point `DATABASE_URL` to your **existing** MariaDB on the host (e.g. `host.docker.internal` on Windows/Mac, or your host IP).

**You will:**
1. Build: `docker build -f docker/Dockerfile -t drum-dungeon .`
2. Run with env vars and a volume for `PRACTICE_DATA_DIR`.
3. Open http://localhost:8000 and test.

**Learning outcome:** You see that the same code runs in a container; only env and volume change.

---

### Step 3.4 — Add MariaDB in Docker (docker-compose)

**What:** Use **Docker Compose** to run app + DB together with one command.

**You will:**
1. Add a `docker-compose.yml` with two services: `app` and `db`.
2. Use Compose **environment** for `DATABASE_URL`, `SESSION_SECRET_KEY`, `PRACTICE_DATA_DIR`.
3. Use **volumes** for DB data and (optionally) practice data.
4. Make the app service **depend on** the DB and wait for it to be ready (e.g. healthcheck or condition).

**Learning outcome:** You understand multi-container setup, volumes, and service dependency.

---

### Step 3.5 — Add healthchecks in Compose

**What:** In `docker-compose.yml`, add a **healthcheck** for the app (e.g. `curl -f http://localhost:8000/health`) and optionally for MariaDB.

**You will:**  
Add `healthcheck` to the app (and DB) service so Compose knows when the service is “ready”.

**Learning outcome:** You see how healthchecks improve startup order and robustness.

---

### Step 3.6 — Document and verify

**What:** Short README or section in `docs/` on how to run with Docker (build, run, env vars, volumes). Then run through: build → up → test app and DB → down.

**Learning outcome:** You have a repeatable, documented way to run the app in Docker.

---

## Order of work (checklist)

- [x] **3.1** Create Dockerfile in `docker/` (base image, install deps, copy app, CMD).
- [ ] **3.2** Create .dockerignore.
- [ ] **3.3** Run app container only, using host MariaDB.
- [ ] **3.4** Add docker-compose.yml (app + db, env, volumes).
- [ ] **3.5** Add healthchecks to docker-compose.
- [ ] **3.6** Document and test full flow.

---

## What we are *not* doing in Phase 3

- No production optimizations (multi-stage builds, non-root user can be added later).
- No Kubernetes or cloud deployment (that would be a later phase).
- No CI/CD building the image (Phase 5).

Phase 3 is only: **run the app and DB in Docker on your machine** and understand why the app is Docker ready and how the Dockerfile and Compose file use that.

When you’re ready, we can implement Step 3.1 (Dockerfile) first and then go through each step one by one.
