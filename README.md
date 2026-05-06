# Drum Dungeon – DevOps Project

## Idea

Drum Dungeon is a browser-based game (webapp) hosted on a VM on a Proxmox node. This repo is the **DevOps track** for that app: the goal is to put in place **CI/CD for staging, production, and future test/updates with zero downtime**. The work is structured in phases so the app stays stable while we add Docker, infrastructure-as-code, pipelines, monitoring, and backups.

---

## What Is Used and Why

| Component | Role |
|-----------|------|
| **FastAPI** | Web framework for the game (API + templates). |
| **PostgreSQL 17** | Persistent storage for users, students, XP, attendance, streaks, history. |
| **Alembic** | Database migrations so schema changes are versioned and repeatable. |
| **Environment variables** | All config and secrets (paths, `DATABASE_URL`, `SESSION_SECRET_KEY`, etc.) so the same code runs locally, in Docker, and on VMs. |
| **Terraform (`bpg/proxmox`)** | Provision Proxmox LXCs (`app-staging`, `app-prod`, `db-prod`) on `momo`. |
| **Ansible** | Configure baseline OS, PostgreSQL, JSON migration, and app systemd service. |
| **(Planned)** GitHub Actions | CI (tests, lint) and CD (deploy to staging/prod) with optional manual approval for prod. |
| **(Planned)** Monitoring & backups | Observability and data safety. |

---

## Phases (Plan)

- **Phase 2.4 — DB implementation**  
  Models, Alembic, connection pooling, health check endpoint. *(Done.)*

- **Phase 2.5 — Secrets management**  
  No hardcoded credentials; env vars and `.env.example`. *(Done.)*

- **Phase 3 — Dockerization**  
  Dockerfile, `.dockerignore`, docker-compose (app + PostgreSQL 17), healthchecks, docs and tests. *(Done.)*

- **Phase 4 — Infrastructure**  
  Terraform (Proxmox LXCs + outputs), Ansible (inventory from Terraform, playbooks, roles, vault).

- **Phase 5 — CI/CD**  
  GitHub Actions: CI on PR, deploy to staging on push to main, deploy to prod (manual or tag), zero-downtime strategy.

- **Phase 6 — Monitoring & observability**  
  Metrics, structured logging, alerting, dashboards.

- **Phase 7 — Data safety & backups**  
  Automated DB backups, retention, restore tests, disaster-recovery docs.

---

## Current Status

- **Phases 2.4, 2.5, 3** are complete: env-based app config and containerized workflow are available.
- **Phase 4 (Phase 1 automation)** now includes Terraform LXC provisioning and Ansible roles for common/database/migration/app.
- **Next:** Phase 5 (GitHub Actions CI/CD pipeline wiring).

---

## Project Structure

```
drum-dungeon-devops/
├── app/                    # FastAPI application
├── alembic/                # Database migrations
├── docker/                 # Dockerfile
├── docker-compose.yml      # Local app + DB workflow
├── terraform/proxmox/      # Proxmox LXCs (app-staging, app-prod, db-prod)
├── ansible/                # Inventory + playbooks + roles (common, database, migration, app)
├── docs/                   # Documentation and phase plans
├── .env.example            # Env template
└── README.md
```

---

## Quick Links

- **Terraform + Ansible (Phase 1):**
  ```bash
  cd terraform/proxmox
  terraform init
  terraform plan -var-file="secrets.tfvars"
  terraform apply -var-file="secrets.tfvars" -auto-approve
  cd ../../ansible
  ansible-galaxy collection install -r requirements.yml
  ansible-playbook -i inventory.yml playbooks/phase1.yml --ask-vault-pass
  ```

## Phase 4 Completion Notes

- Proxmox LXCs provisioned on node `momo`: `app-staging`, `app-prod`, `db-prod`.
- PostgreSQL 17 installed and configured on `db-prod` with migrated student/user data.
- App deployed to `/opt/app` on staging and prod via Ansible, running under `systemd`.
- Runtime fixes applied for modern FastAPI/Starlette template rendering and DB-aware data reads.
- Both app nodes now report healthy DB-connected status on `/health`.
