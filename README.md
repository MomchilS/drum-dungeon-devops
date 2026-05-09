# Drum Dungeon DevOps Project

Drum Dungeon is a FastAPI browser app deployed on Proxmox LXCs with PostgreSQL-backed runtime data, Ansible operations, GitHub Actions CI/CD, monitoring, and PBS backups.

This repository is the complete DevOps track for the app: infrastructure provisioning, configuration management, deployment automation, runtime documentation, and safe staging-to-production promotion.

## Final Status

The project is functionally complete.

| Area | Status |
| --- | --- |
| App cleanup and stabilization | Complete |
| PostgreSQL-only runtime refactor | Complete |
| Terraform Proxmox infrastructure | Complete |
| Ansible staging and production deploys | Complete |
| Separate staging and production databases | Complete |
| GitHub Actions CI | Complete |
| Automatic staging deploy on push to `main` | Complete |
| Manual production deploy with approval | Complete |
| Monitoring stack | Complete |
| Automated PBS backups | Complete |

## Architecture

```text
GitHub main branch
  |
  |-- CI workflow: compile and test
  |-- Deploy Staging workflow: automatic app deploy to app-staging
  `-- Deploy Production workflow: manual approved app deploy to app-prod

Proxmox node momo
  |-- app-staging LXC  -> FastAPI/Uvicorn/systemd, staging app
  |-- app-prod LXC     -> FastAPI/Uvicorn/systemd, production app
  |-- db-prod LXC      -> PostgreSQL 17, separate staging/prod databases
  `-- github-runner   -> self-hosted GitHub Actions runner inside the network
```

## Runtime Stack

| Component | Role |
| --- | --- |
| FastAPI | Web app, routes, templates, admin/student workflows |
| PostgreSQL 17 | Runtime source of truth for users, students, XP, attendance, streaks, and history |
| SQLAlchemy | ORM and database access layer |
| Alembic | Database migration framework |
| Uvicorn + systemd | App runtime on staging and production LXCs |
| Terraform | Provisions Proxmox LXCs |
| Ansible | Configures hosts and deploys the app |
| GitHub Actions | CI, automatic staging deploy, manual production deploy |
| Proxmox Backup Server | Automated backup coverage |

## Environments

| Environment | App host | Database host | Database purpose |
| --- | --- | --- | --- |
| Staging | `app-staging` / `192.168.2.20` | `db-prod` / `192.168.2.22` | `student_db_staging` for testing |
| Production | `app-prod` / `192.168.2.21` | `db-prod` / `192.168.2.22` | `student_db` for live data |

Staging and production share the PostgreSQL LXC but use separate databases and credentials. App deploys do not copy or modify production data.

## CI/CD Flow

### CI

Workflow: `.github/workflows/ci.yml`

Runs on pushes, pull requests, and manual dispatch. It installs Python dependencies, compiles `app` and `tests`, and runs the unit test suite.

### Staging Deploy

Workflow: `.github/workflows/deploy-staging.yml`

Runs automatically on push to `main`, and can also be run manually. It uses the self-hosted runner, creates temporary deploy secrets from the GitHub `Staging` environment, deploys only the Ansible `app` tag to `app-staging`, then checks `/health`.

### Production Deploy

Workflow: `.github/workflows/deploy-production.yml`

Runs only when manually triggered from GitHub Actions. It uses the `Production` GitHub Environment, including required approval/protection rules. It deploys the selected ref, normally the latest `main`, to `app-prod` using only the Ansible `app` tag and then checks `/health`.

If several commits have already been pushed and tested on staging, one manual production deploy from `main` deploys the full latest repository state, including all those commits.

## Safe Operations

From `ansible/`, install required collections:

```bash
ansible-galaxy collection install -r requirements.yml
```

Deploy the app to staging only:

```bash
ansible-playbook -i inventory/phase1.yml playbooks/phase1.yml \
  --ask-vault-pass \
  --tags app \
  --limit app-staging
```

Deploy the app to production only:

```bash
ansible-playbook -i inventory/phase1.yml playbooks/phase1.yml \
  --ask-vault-pass \
  --tags app \
  --limit app-prod
```

Check app health:

```bash
ansible -i inventory/phase1.yml app-staging -u root -b -m uri \
  -a "url=http://127.0.0.1:8000/health return_content=yes status_code=200" \
  --ask-vault-pass

ansible -i inventory/phase1.yml app-prod -u root -b -m uri \
  -a "url=http://127.0.0.1:8000/health return_content=yes status_code=200" \
  --ask-vault-pass
```

Do not include `db` or `migrate` tags in routine CI/CD app deploys. Database and migration tasks are explicit maintenance/bootstrap operations only.

## Data Model

PostgreSQL is the only runtime data source for staging and production. JSON files and JSON-oriented scripts, where still present, are retained only for legacy maintenance, import/export, or historical reference. They are not a live fallback for authentication or student data.

## Secrets

Secrets are split by responsibility:

- Terraform secrets and local tfvars stay local and are ignored by Git.
- Ansible runtime secrets are stored in environment-specific vault files for manual operations.
- GitHub Actions deployment secrets are stored in GitHub Environments: `Staging` and `Production`.
- SSH private keys, vault passwords, DB passwords, and session secrets must never be committed.

The `.gitignore` excludes local env files, vault files, Terraform state/tfvars, private keys, and other local secret material.

## Repository Map

```text
app/                    FastAPI app, templates, services, models, runtime scripts
alembic/                Database migrations
docker/                 App Dockerfile retained for image/build support
terraform/              Proxmox infrastructure definitions
ansible/                Inventory, playbooks, roles, vault structure, deploy runbooks
.github/workflows/      CI, staging deploy, production deploy workflows
tests/                  Unit tests for PostgreSQL-only runtime behavior
```

See the folder-level READMEs for operational details.
