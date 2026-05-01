# Proxmox LXCs (Phase 1)

Creates three LXCs on node `momo`:
- `app-staging` (1 core, 1024 MB RAM)
- `app-prod` (1 core, 2048 MB RAM)
- `db-prod` (1 core, 2048 MB RAM)

## Prerequisites

- Proxmox API token with permissions to create LXCs
- LXC template available: `local:vztmpl/debian-13-standard_13.1-2_amd64.tar.zst`
- Terraform >= 1.0

## Usage

1. Copy and fill variables:
   ```bash
   cp terraform.tfvars.example secrets.tfvars
   # Edit secrets.tfvars with Proxmox API token and SSH key
   ```

2. Init and apply:
   ```bash
   terraform init
   terraform plan -var-file="secrets.tfvars"
   terraform apply -var-file="secrets.tfvars"
   ```

3. Inspect generated outputs:
   ```bash
   terraform output phase1_container_ips
   terraform output -json phase1_inventory_hosts
   ```

Ansible inventory reads `phase1_inventory_hosts` directly through `ansible/scripts/terraform_inventory.py`.
