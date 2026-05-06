# Ansible — Phase 1 deployment

Phase 1 configures three Proxmox LXCs:
- `app-staging`
- `app-prod`
- `db-prod`

## Prerequisites

- Ansible Core (or Ansible) 2.14+
- Collections: `ansible-galaxy collection install -r requirements.yml`
- Terraform has already applied from `terraform/proxmox`
- SSH access to the created LXCs

## Inventory

Primary day-to-day deploy commands in this repo use static inventory:

```bash
-i inventory/phase1.yml
```

This avoids coupling routine app deploys to local Terraform state output.

`inventory.yml` still exists and uses `scripts/terraform_inventory.py`, which calls:

```bash
terraform output -json phase1_inventory_hosts
```

That means inventory is pulled from Terraform outputs directly.

## Secrets (Vault)

Primary vault structure is environment-specific:

1. `cp group_vars/staging/vault.example.yml group_vars/staging/vault.yml`
2. `cp group_vars/production/vault.example.yml group_vars/production/vault.yml`
3. Edit both with real `db_user`, `db_password`, `session_secret_key`
4. Encrypt each:
   - `ansible-vault encrypt group_vars/staging/vault.yml`
   - `ansible-vault encrypt group_vars/production/vault.yml`
5. Run playbooks with `--ask-vault-pass` so Ansible can read the secrets.

## Playbooks

From the `ansible` directory:

**Canonical app deploy workflow (explicit per environment):**
```bash
ansible-playbook -i inventory/phase1.yml playbooks/phase1.yml --ask-vault-pass --tags app --limit app-staging
ansible-playbook -i inventory/phase1.yml playbooks/phase1.yml --ask-vault-pass --tags app --limit app-prod
```

**Infrastructure/bootstrap runs (shared DB host):**
```bash
ansible-playbook -i inventory/phase1.yml playbooks/phase1.yml --ask-vault-pass --tags common
ansible-playbook -i inventory/phase1.yml playbooks/phase1.yml --ask-vault-pass --tags db
ansible-playbook -i inventory/phase1.yml playbooks/phase1.yml --ask-vault-pass --tags migrate
```

## Validation commands

Use these checks after deploys:

```bash
ansible -i inventory/phase1.yml app-staging -u root -b -m shell -a "grep -E '^(DB_HOST|DB_PORT|DB_NAME|DB_USER|SESSION_SECRET_KEY)=' /opt/app/.env" --ask-vault-pass
ansible -i inventory/phase1.yml app-prod -u root -b -m shell -a "grep -E '^(DB_HOST|DB_PORT|DB_NAME|DB_USER|SESSION_SECRET_KEY)=' /opt/app/.env" --ask-vault-pass
```

## Legacy playbooks (kept for reference)

The following playbooks are retained but are not the canonical deployment path:

- `playbooks/deploy-app.yml`
- `playbooks/common.yml`

## Role summary

- **common** — Updates apt, sets timezone, and installs baseline packages (`python3-pip`, `libpq-dev`, `git`).
- **database** — Installs PostgreSQL 17, configures remote access, and creates `student_db`.
- **migration** — Uploads `students_data` and migrates JSON content into PostgreSQL tables.
- **app** — Syncs code to `/opt/app`, builds venv, writes env file, and manages app with systemd.
