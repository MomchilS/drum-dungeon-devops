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

`inventory.yml` uses `scripts/terraform_inventory.py`, which calls:

```bash
terraform output -json phase1_inventory_hosts
```

That means inventory is pulled from Terraform outputs directly.

## Secrets (Vault)

Create vault files for staging and production:

1. `cp group_vars/staging/vault.example.yml group_vars/staging/vault.yml`
2. `cp group_vars/production/vault.example.yml group_vars/production/vault.yml`
3. Edit both with real `db_user`, `db_password`, `session_secret_key`
4. Encrypt each:
   - `ansible-vault encrypt group_vars/staging/vault.yml`
   - `ansible-vault encrypt group_vars/production/vault.yml`
4. Run playbooks with `--ask-vault-pass` so Ansible can read the secrets.

## Playbooks

From the `ansible` directory:

**Run full Phase 1 automation:**
```bash
ansible-playbook -i inventory.yml playbooks/phase1.yml --ask-vault-pass
```

**Optional targeted runs by tag:**
```bash
ansible-playbook -i inventory.yml playbooks/phase1.yml --ask-vault-pass --tags common
ansible-playbook -i inventory.yml playbooks/phase1.yml --ask-vault-pass --tags db
ansible-playbook -i inventory.yml playbooks/phase1.yml --ask-vault-pass --tags migrate
ansible-playbook -i inventory.yml playbooks/phase1.yml --ask-vault-pass --tags app
```

## Role summary

- **common** — Updates apt, sets timezone, and installs baseline packages (`python3-pip`, `libpq-dev`, `git`).
- **database** — Installs PostgreSQL 17, configures remote access, and creates `student_db`.
- **migration** — Uploads `students_data` and migrates JSON content into PostgreSQL tables.
- **app** — Syncs code to `/opt/app`, builds venv, writes env file, and manages app with systemd.
