# =============================================================================
# Drum Dungeon - Dockerfile (Step 3.1)
# Build from repo root: docker build -f docker/Dockerfile -t drum-dungeon .
# Run with:            docker run -p 8000:8000 --env-file .env drum-dungeon
# =============================================================================

# -----------------------------------------------------------------------------
# Base image: the starting point for every layer below.
# python:3.11-slim = official Python 3.11 on a minimal Debian-based OS.
# "slim" = smaller image (no build tools, fewer packages) = faster pulls, less disk.
# -----------------------------------------------------------------------------
FROM python:3.11-slim

# -----------------------------------------------------------------------------
# Set the working directory inside the container.
# All following RUN, COPY, CMD commands run from /app unless you use an absolute path.
# Like doing "cd /app" and keeping that for the rest of the Dockerfile.
# -----------------------------------------------------------------------------
WORKDIR /app

# -----------------------------------------------------------------------------
# Copy ONLY the dependency file first (not the whole app yet).
# We do this separately so Docker can cache this layer: when requirements.txt
# doesn't change, "pip install" is not re-run. When you change code, only the
# COPY app/ step is re-run. This makes rebuilds much faster.
# -----------------------------------------------------------------------------
COPY app/requirements.txt .

# -----------------------------------------------------------------------------
# Install Python dependencies into the container's Python environment.
# --no-cache-dir = don't store pip's download cache in the image (keeps image smaller).
# -r requirements.txt = install every package listed in that file.
# -----------------------------------------------------------------------------
RUN pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------------------------
# Copy the application code into the image.
# app/ = everything inside the app/ folder (main.py, config.py, templates/, etc.).
# ./app/ = place it at /app/app/ inside the container.
# So we get /app/app/main.py, /app/app/config.py, ... and "app" is a Python package.
# -----------------------------------------------------------------------------
COPY app/ ./app/

# -----------------------------------------------------------------------------
# Copy Alembic so we can run migrations inside the container later if we want.
# alembic/ = migration scripts, alembic.ini = config. Placed at /app/alembic/ and /app/alembic.ini.
# -----------------------------------------------------------------------------
COPY alembic/ ./alembic/
COPY alembic.ini .

# -----------------------------------------------------------------------------
# Tell the container which port the app listens on.
# This is documentation only; it doesn't publish the port. "docker run -p 8000:8000" does that.
# -----------------------------------------------------------------------------
EXPOSE 8000

# -----------------------------------------------------------------------------
# Default command when the container starts.
# exec form (JSON array) = no shell wrapper, so the process gets signals correctly (e.g. SIGTERM for graceful shutdown).
# uvicorn app.main:app = run the FastAPI "app" object from the "app.main" module.
# --host 0.0.0.0 = listen on all interfaces (required in Docker; 127.0.0.1 would only accept connections from inside the container).
# --port 8000 = listen on port 8000.
# -----------------------------------------------------------------------------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
