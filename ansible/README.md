# Ansible

Ansible configures and deploys the Drum Dungeon staging and production environments.

## Hosts and Inventory

Primary inventory:

```bash
-i inventory/phase1.yml
```

Current static host layout:

| Host | IP | Role |
| --- | --- | --- |
| `app-staging` | `192.168.2.20` | Staging app LXC |
| `app-prod` | `192.168.2.21` | Production app LXC |
| `db-prod` | `192.168.2.22` | PostgreSQL 17 LXC |

Static inventory is used for day-to-day operations so app deploys do not depend on local Terraform state. Dynamic inventory support remains available through `inventory.yml` and `scripts/terraform_inventory.py`.

## Roles

| Role | Purpose |
| --- | --- |
| `common` | Baseline OS packages and host setup |
| `database` | PostgreSQL 17 installation, access configuration, database/user setup |
| `migration` | Explicit JSON-to-PostgreSQL import/bootstrap helper |
| `app` | Syncs code to `/opt/app`, creates venv, writes `.env`, installs systemd unit, starts app |

## Main Playbook

Primary playbook:

```bash
playbooks/phase1.yml
```

It contains separate plays for baseline setup, database setup, migration, staging app deploy, and production app deploy.

## Secrets

Manual operations use environment-specific vault files:

```text
group_vars/staging/vault.yml
group_vars/production/vault.yml
```

These files are ignored by Git and should be encrypted with Ansible Vault. They contain environment-specific DB credentials and `session_secret_key` values.

GitHub Actions deploys use GitHub Environment secrets to generate temporary vault vars during workflow runs. Those generated files are deleted by the workflow and must not be committed.

## Routine App Deploys

From `ansible/`, install collections:

```bash
ansible-galaxy collection install -r requirements.yml
```

Deploy staging app only:

```bash
ansible-playbook -i inventory/phase1.yml playbooks/phase1.yml \
  --ask-vault-pass \
  --tags app \
  --limit app-staging
```

Deploy production app only:

```bash
ansible-playbook -i inventory/phase1.yml playbooks/phase1.yml \
  --ask-vault-pass \
  --tags app \
  --limit app-prod
```

These commands sync the app, install dependencies, write the environment file, and manage the `drum-dungeon` systemd service.

## Health Checks

```bash
ansible -i inventory/phase1.yml app-staging -u root -b -m uri \
  -a "url=http://127.0.0.1:8000/health return_content=yes status_code=200" \
  --ask-vault-pass

ansible -i inventory/phase1.yml app-prod -u root -b -m uri \
  -a "url=http://127.0.0.1:8000/health return_content=yes status_code=200" \
  --ask-vault-pass
```

Check deployed DB target without printing passwords:

```bash
ansible -i inventory/phase1.yml app-staging -u root -b -m shell \
  -a "grep -E '^(ENV|DB_HOST|DB_PORT|DB_NAME|DB_USER)=' /opt/app/.env" \
  --ask-vault-pass

ansible -i inventory/phase1.yml app-prod -u root -b -m shell \
  -a "grep -E '^(ENV|DB_HOST|DB_PORT|DB_NAME|DB_USER)=' /opt/app/.env" \
  --ask-vault-pass
```

## CI/CD Relationship

GitHub Actions calls Ansible from the self-hosted runner:

- `deploy-staging.yml` runs automatically on push to `main` and targets `app-staging`.
- `deploy-production.yml` runs manually with the `Production` environment and targets `app-prod`.

Both workflows deploy only the `app` tag. They do not run database or migration tasks.

## Safety Notes

Do not run these casually in CI/CD:

```bash
--tags db
--tags migrate
```

Use database and migration tags only for intentional infrastructure/bootstrap maintenance. Routine code releases should use app-only deploys.
