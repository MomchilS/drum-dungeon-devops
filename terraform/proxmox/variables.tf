variable "proxmox_api_url" {
  description = "Proxmox API URL (e.g. https://192.168.1.10:8006/api2/json)"
  type        = string
}

variable "proxmox_api_token_id" {
  description = "Proxmox API token ID (e.g. user@pam!terraform)"
  type        = string
  sensitive   = true
}

variable "proxmox_api_token_secret" {
  description = "Proxmox API token secret"
  type        = string
  sensitive   = true
}

variable "proxmox_insecure" {
  description = "Skip TLS verification for Proxmox API (use true for self-signed)"
  type        = bool
  default     = true
}

variable "proxmox_node" {
  description = "Proxmox node name where LXCs will be created"
  type        = string
  default     = "momo"
}

variable "lxc_template" {
  description = "LXC template file id"
  type        = string
  default     = "local:vztmpl/debian-13-standard_13.1-2_amd64.tar.zst"
}

variable "rootfs_storage" {
  description = "Storage datastore used for LXC root filesystem"
  type        = string
  default     = "local-lvm"
}

variable "app_rootfs_size_gb" {
  description = "Root filesystem size for app LXCs in GB"
  type        = number
  default     = 16
}

variable "db_rootfs_size_gb" {
  description = "Root filesystem size for db LXC in GB"
  type        = number
  default     = 20
}

variable "app_staging_vm_id" {
  description = "Container ID for app-staging"
  type        = number
  default     = 201
}

variable "app_prod_vm_id" {
  description = "Container ID for app-prod"
  type        = number
  default     = 202
}

variable "db_prod_vm_id" {
  description = "Container ID for db-prod"
  type        = number
  default     = 203
}

variable "network_bridge" {
  description = "Proxmox bridge for LXC network"
  type        = string
  default     = "vmbr0"
}

variable "ssh_public_key" {
  description = "Public SSH key injected into LXC root account"
  type        = string
}
