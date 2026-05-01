terraform {
  required_version = ">= 1.0"
  required_providers {
    proxmox = {
      source  = "bpg/proxmox"
      version = "~> 0.70"
    }
  }
}

provider "proxmox" {
  endpoint  = var.proxmox_api_url
  api_token = "${var.proxmox_api_token_id}=${var.proxmox_api_token_secret}"
  insecure  = var.proxmox_insecure
}

locals {
  lxc_definitions = {
    app-staging = {
      vm_id      = var.app_staging_vm_id
      memory     = 1024
      disk_size  = var.app_rootfs_size_gb
      boot_order = 10
    }
    app-prod = {
      vm_id      = var.app_prod_vm_id
      memory     = 2048
      disk_size  = var.app_rootfs_size_gb
      boot_order = 20
    }
    db-prod = {
      vm_id      = var.db_prod_vm_id
      memory     = 2048
      disk_size  = var.db_rootfs_size_gb
      boot_order = 30
    }
  }
}

resource "proxmox_virtual_environment_container" "phase1" {
  for_each = local.lxc_definitions

  node_name    = var.proxmox_node
  vm_id        = each.value.vm_id
  unprivileged = true
  started      = true

  startup {
    order    = each.value.boot_order
    up_delay = 20
  }

  initialization {
    hostname = each.key
    user_account {
      keys = [var.ssh_public_key]
    }
    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }
  }

  cpu {
    cores = 1
  }

  memory {
    dedicated = each.value.memory
    swap      = 512
  }

  disk {
    datastore_id = var.rootfs_storage
    size         = each.value.disk_size
  }

  network_interface {
    name   = "eth0"
    bridge = var.network_bridge
  }

  operating_system {
    template_file_id = var.lxc_template
    type             = "debian"
  }

  tags = ["phase1", "drum-dungeon", replace(each.key, "-", "_")]
}
