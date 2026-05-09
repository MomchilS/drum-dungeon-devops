# Docker

This folder contains the app Dockerfile.

## Current Role

Docker support is retained for building the FastAPI app image and for future container-based workflows. The current staging and production runtime does not use the old local Docker Compose stack.

Production and staging currently run as:

```text
FastAPI app -> Uvicorn -> systemd -> Proxmox LXC
```

with PostgreSQL 17 on the shared `db-prod` LXC.

## Dockerfile

`Dockerfile` builds a Python image that:

- installs `app/requirements.txt`
- copies `app/`
- copies Alembic files
- exposes port `8000`
- starts Uvicorn with `app.main:app`

Example build from the repository root:

```bash
docker build -f docker/Dockerfile -t drum-dungeon-app .
```

## Removed Legacy Flow

The old local MariaDB Docker Compose flow was removed. PostgreSQL is the supported runtime database, and deployed app environments are managed through Ansible and GitHub Actions.
