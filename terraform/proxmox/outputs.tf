output "phase1_container_ips" {
  description = "IPv4 addresses discovered from LXC interfaces"
  value = {
    for name, container in proxmox_virtual_environment_container.phase1 :
    name => try(
      [
        for ip in flatten(container.network_interface[*].ipv4_addresses) :
        ip if ip != null && ip != ""
      ][0],
      null
    )
  }
}

output "phase1_inventory_hosts" {
  description = "Host map consumed by Ansible inventory generator"
  value = {
    for name, container in proxmox_virtual_environment_container.phase1 :
    name => {
      vm_id = container.vm_id
      ip = try(
        [
          for addr in flatten(container.network_interface[*].ipv4_addresses) :
          addr if addr != null && addr != ""
        ][0],
        null
      )
      groups = contains(["app-staging", "app-prod"], name) ? ["app", "all_phase1"] : ["db", "all_phase1"]
    }
  }
}
