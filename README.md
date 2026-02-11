# Drum Dungeon – DevOps Project

## Idea

Drum Dungeon is a browser-based game (webapp) hosted on a VM on a Proxmox node. This repo is the **DevOps track** for that app: the goal is to put in place **CI/CD for staging, production, and future test/updates with zero downtime**. The work is structured in phases so the app stays stable while we add Docker, infrastructure-as-code, pipelines, monitoring, and backups.

---

## What Is Used and Why

| Component | Role |
|-----------|------|
| **FastAPI** | Web framework for the game (API + templates). |
| **MariaDB** | Persistent storage for users, students, XP, attendance, streaks, history (replacing JSON-only over time). |
| **Alembic** | Database migrations so schema changes are versioned and repeatable. |
| **Environment variables** | All config and secrets (paths, `DATABASE_URL`, `SESSION_SECRET_KEY`, etc.) so the same code runs locally, in Docker, and on VMs. |
| **Docker** | Run app and DB in containers; same image runs anywhere. |
| **Docker Compose** | One command to run app + MariaDB with healthchecks and volumes. |
| **(Planned)** Terraform + Ansible | Provision VMs on Proxmox and deploy the app. |
| **(Planned)** GitHub Actions | CI (tests, lint) and CD (deploy to staging/prod) with optional manual approval for prod. |
| **(Planned)** Monitoring & backups | Observability and data safety. |

---

## Phases (Plan)

- **Phase 2.4 — DB implementation**  
  Models, Alembic, connection pooling, health check endpoint. *(Done.)*

- **Phase 2.5 — Secrets management**  
  No hardcoded credentials; env vars and `.env.example`. *(Done.)*

- **Phase 3 — Dockerization**  
  Dockerfile, `.dockerignore`, docker-compose (app + MariaDB), healthchecks, docs and tests. *(Done.)*

- **Phase 4 — Infrastructure**  
  Terraform (Proxmox VMs, tags, outputs), Ansible (inventory, playbooks, roles, vault for secrets).

- **Phase 5 — CI/CD**  
  GitHub Actions: CI on PR, deploy to staging on push to main, deploy to prod (manual or tag), zero-downtime strategy.

- **Phase 6 — Monitoring & observability**  
  Metrics, structured logging, alerting, dashboards.

- **Phase 7 — Data safety & backups**  
  Automated DB backups, retention, restore tests, disaster-recovery docs.

---

## Current Status

- **Phases 2.4, 2.5, 3** are complete: app runs with MariaDB, env-based config, Docker image, and Compose (app + DB). See [docs/docker-summary.md](docs/docker-summary.md) and [docs/docker-run.md](docs/docker-run.md) for the Docker workflow.
- **Next:** Phase 4 (Terraform + Ansible).

---

## Project Structure

```
drum-dungeon-devops/
├── app/                    # FastAPI application
├── alembic/                 # Database migrations
├── docker/                  # Dockerfile
├── docs/                    # Documentation (incl. Docker and phase plans)
├── docker-compose.yml       # App + MariaDB
├── .env.example             # Env template
└── README.md
```

---

## Quick Links

- **Local run:** `.env` from `.env.example`, `python create_db.py`, `alembic upgrade head`, then run uvicorn from `app/`.
- **Docker run:** `cp .env.example .env`, set secrets, `docker compose up -d --build`, then create initial admin (see [docs/docker-run.md](docs/docker-run.md)).
