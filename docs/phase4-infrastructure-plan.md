# Phase 4 — Infrastructure (Terraform + Ansible): Step-by-Step Plan

This document explains **what** we do in Phase 4, **in what order**, and **why**. The goal is to create the **staging** and **prod** VMs on your Proxmox node and configure them so the Drum Dungeon app (Docker Compose) can be deployed there. The current host VM stays as admin-only; we do not modify it with Terraform.

---

## 1. Why Terraform and Ansible Together?

| Tool | Responsibility | Why |
|------|----------------|-----|
| **Terraform** | **Provision** — Create VMs on Proxmox (CPU, RAM, disks, network). | Infrastructure-as-code: same VMs every time; you can recreate or add VMs by changing config and running `terraform apply`. Outputs (e.g. VM IPs) feed into the next step. |
| **Ansible** | **Configure** — Install Docker, set firewall, deploy app, create users. | Configuration-as-code: same setup on every VM; idempotent (safe to run repeatedly). Uses Terraform outputs (IPs) as inventory so you don’t hardcode IPs. |

So: **Terraform = “create the machines”; Ansible = “set up the machines and deploy the app”.**

---

## 2. What We Need Before Starting

- **Proxmox API access**  
  - Either: API token (user + token ID + secret) with permissions to create VMs, clone templates, use storage.  
  - Or: username + password (less ideal; token is better for automation).  
  - The machine that runs Terraform (e.g. your PC or the admin VM) must reach the Proxmox API (e.g. `https://proxmox-ip:8006`).

- **A VM template on Proxmox**  
  - e.g. Ubuntu 24.04 cloud image, converted to a Proxmox template.  
  - Terraform will **clone** this template to create staging and prod VMs (fast, consistent).

- **Terraform and Ansible installed**  
  - On the machine from which you run Phase 4 (e.g. Ubuntu 24 on your PC or admin VM): `terraform` (v1.x) and `ansible-core` (or `ansible`).

- **Storage names**  
  - Your Proxmox storage names (e.g. `local-lvm`, `lvmthin`, or an NVMe + LVM-thin setup). We’ll use variables so you can set them once.

- **Network**  
  - Which bridge the VMs use (e.g. `vmbr0`) and how they get IPs (DHCP or static). For Ansible we need reachable IPs (DHCP reservations or static in Terraform/cloud-init).

---

## 3. Step-by-Step Order of Work

### Step 4.1 — Terraform: provider and variables

**What:** Configure the Proxmox provider and define variables (node name, template name, storage, network).

**Why:** So Terraform can talk to your Proxmox and all VM options are in one place (no magic strings in VM resources).

**Deliverable:** `terraform/proxmox/provider.tf` (or `main.tf`), `variables.tf`, `terraform.tfvars.example` (you copy to `terraform.tfvars` and fill in secrets; `terraform.tfvars` is in `.gitignore`).

---

### Step 4.2 — Terraform: create staging and prod VMs

**What:** Define two VMs (e.g. `drum-dungeon-staging`, `drum-dungeon-prod`), each with:
- Clone from the Ubuntu (or chosen) template.
- CPU, RAM (e.g. 2 cores, 4 GB to start).
- Disks: e.g. one for OS (≈50G on fast storage if you have it), one for data (e.g. 100–200G on LVM-thin).
- Network on the right bridge.
- Tags/labels (e.g. `environment=staging` / `environment=prod`) so you can see which is which in Proxmox.

**Why:** So both environments exist in one `terraform apply`; same layout for staging and prod.

**Deliverable:** `terraform/proxmox/vms.tf` (or merged into `main.tf`), and **outputs** for the VM IPs (and optionally VM IDs). We need IPs for Ansible.

---

### Step 4.3 — Terraform: outputs for Ansible

**What:** Output the public or management IP of each VM (e.g. `staging_ip`, `prod_ip`).

**Why:** Ansible needs to know **where** to SSH. We can either:
- Use Terraform’s outputs to generate an Ansible inventory file, or
- Use a static inventory and paste the IPs after the first apply.

Starting with a **static inventory** is simpler; we’ll document “after `terraform apply`, put these IPs in `ansible/inventory/staging.yml` and `production.yml`”.

**Deliverable:** `outputs.tf` and a short note in the Phase 4 doc to update inventory with the IPs.

---

### Step 4.4 — Ansible: inventory and group_vars

**What:**
- **Inventory:** `ansible/inventory/staging.yml` and `ansible/inventory/production.yml` (or one file with groups). Each host: IP (or hostname), SSH user (e.g. `ubuntu` for cloud image).
- **group_vars:** `ansible/group_vars/staging.yml` and `ansible/group_vars/production.yml` for environment-specific variables (e.g. `app_env: staging` vs `prod`, domain, or any future flags).

**Why:** So Ansible knows which hosts are staging vs prod and can use different vars per environment (e.g. different `SESSION_SECRET_KEY` in prod).

**Deliverable:** Inventory files and group_vars files (can be minimal at first).

---

### Step 4.5 — Ansible: “common” playbook (Docker, firewall, users)

**What:** A playbook (e.g. `ansible/playbooks/common.yml`) that runs on all app VMs and:
- Ensures Docker and Docker Compose (plugin) are installed.
- Configures firewall (e.g. allow SSH + port 8000; deny everything else by default).
- Optionally: create a non-root user, add SSH keys.

**Why:** Every staging and prod VM should have the same base: Docker available and only needed ports open.

**Deliverable:** `ansible/playbooks/common.yml` and a role (e.g. `ansible/roles/docker`) if we want to keep tasks reusable.

---

### Step 4.6 — Ansible: “deploy-app” playbook

**What:** A playbook (e.g. `ansible/playbooks/deploy-app.yml`) that:
- Copies the repo (or the needed files: `docker-compose.yml`, `docker/`, `.env`) onto the VM, or clones the repo.
- Ensures `.env` is present (from a template or from Ansible Vault).
- Runs `docker compose up -d --build` (or equivalent) so the app and DB start.

**Why:** So we can deploy or update the app on staging/prod with one command (`ansible-playbook deploy-app.yml -l staging`), without logging in manually.

**Deliverable:** `ansible/playbooks/deploy-app.yml` and optionally a role `ansible/roles/app`.

---

### Step 4.7 — Ansible: secrets (Vault)

**What:** Put secrets (e.g. `DB_ROOT_PASSWORD`, `SESSION_SECRET_KEY`) in an encrypted file (Ansible Vault) and reference them in playbooks/roles (e.g. when building `.env` on the VM).

**Why:** So we don’t store prod secrets in plain text in the repo; only the vault password is needed to run playbooks.

**Deliverable:** `ansible/group_vars/production/vault.yml` (encrypted), and a note in the doc to create it with `ansible-vault create` and to pass `--ask-vault-pass` when running playbooks. Staging can use a separate vault or the same file with different vars.

---

## 4. Suggested Directory Layout

```
terraform/
  proxmox/
    main.tf          # provider + VMs (or split into provider.tf, vms.tf)
    variables.tf
    outputs.tf
    terraform.tfvars.example
ansible/
  inventory/
    staging.yml
    production.yml
  group_vars/
    staging.yml
    production.yml
    production/
      vault.yml      # encrypted
  playbooks/
    common.yml       # Docker, firewall, users
    deploy-app.yml   # deploy app
  roles/
    docker/
    app/
```

---

## 5. Order of Execution (When You Run It)

1. **Fill in Terraform variables** (copy `terraform.tfvars.example` → `terraform.tfvars`, set Proxmox URL, token, node, template, storage).
2. **Run Terraform:** `terraform init`, `terraform plan`, `terraform apply` → creates staging and prod VMs.
3. **Get IPs** from Terraform outputs and put them in Ansible inventory.
4. **Create vault:** `ansible-vault create group_vars/production/vault.yml` and add secrets.
5. **Run common playbook:** `ansible-playbook playbooks/common.yml -i inventory/staging.yml` (then for production) so Docker and firewall are set.
6. **Deploy app:** `ansible-playbook playbooks/deploy-app.yml -i inventory/staging.yml` (then production when ready).

---

## 6. What We Are *Not* Doing in Phase 4

- **Monitoring VM** — We’ll add that in Phase 6 (Prometheus/Grafana).
- **Changing the current (admin) VM** — Terraform only creates the two new VMs (staging + prod).
- **Cloudflare / DNS** — You’ll point Cloudflare tunnel to the prod VM IP after migration and validation; no automation for that in Phase 4 unless you ask for it later.
- **CI/CD** — That’s Phase 5 (GitHub Actions will call Ansible or Docker deploy later).

---

## 7. Checklist (Phase 4)

- [x] **4.1** Terraform: provider + variables (+ tfvars.example).
- [x] **4.2** Terraform: staging and prod VMs (clone template, CPU/RAM/disks/network/tags).
- [x] **4.3** Terraform: outputs (VM IDs; IPs from Proxmox → Ansible inventory).
- [x] **4.4** Ansible: inventory (staging, production) + group_vars.
- [x] **4.5** Ansible: common playbook (Docker, firewall).
- [x] **4.6** Ansible: deploy-app playbook + app role (clone repo, .env from vault, docker compose up).
- [x] **4.7** Ansible: vault.example for production and staging; you encrypt vault.yml.
- [x] **4.8** Document: README in terraform/proxmox and ansible/; Phase 4 plan doc.

**Your next steps:** Create a Proxmox API token and VM template, fill `terraform.tfvars`, run Terraform, put VM IPs in Ansible inventory, create and encrypt vault.yml, run common then deploy-app playbooks. Then run the JSON→MariaDB migration on staging, validate, then prod and point Cloudflare at prod.
