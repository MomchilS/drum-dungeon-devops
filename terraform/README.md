# Terraform

Terraform provisions the Proxmox LXC infrastructure used by the project.

## Scope

The active Terraform configuration is in `terraform/proxmox/` and creates the core LXCs on Proxmox node `momo`:

| LXC | Role |
| --- | --- |
| `app-staging` | Staging FastAPI app host |
| `app-prod` | Production FastAPI app host |
| `db-prod` | PostgreSQL 17 host for separate staging and production databases |

A separate `github-runner` LXC is used as the self-hosted GitHub Actions runner inside the same network.

## Inputs

Terraform requires Proxmox connection details and deployment settings such as:

- Proxmox API URL
- Proxmox API token ID and secret
- Proxmox node name
- LXC template ID
- root filesystem storage
- SSH public key injected into the LXC root account

Use `terraform/proxmox/terraform.tfvars.example` as the template for local values.

## Safe Commands

From `terraform/proxmox/`:

```bash
terraform init
terraform plan -var-file="secrets.tfvars"
terraform apply -var-file="secrets.tfvars"
```

Inspect outputs:

```bash
terraform output phase1_container_ips
terraform output -json phase1_inventory_hosts
```

## Safety Notes

Do not commit:

- `*.tfvars`
- Terraform state files
- Terraform plans
- API tokens
- private keys

These are ignored by `.gitignore` and should remain local secret/state material.

Routine app deployments should use Ansible or GitHub Actions, not Terraform. Terraform is for infrastructure lifecycle changes.
