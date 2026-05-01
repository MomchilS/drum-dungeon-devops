#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path


def load_hosts():
    repo_root = Path(__file__).resolve().parents[2]
    terraform_dir = repo_root / "terraform" / "proxmox"

    cmd = ["terraform", "output", "-json", "phase1_inventory_hosts"]
    proc = subprocess.run(
        cmd,
        cwd=terraform_dir,
        check=True,
        text=True,
        capture_output=True,
    )
    output = json.loads(proc.stdout)
    return output["value"] if isinstance(output, dict) and "value" in output else output


def build_inventory():
    hosts = load_hosts()
    inventory = {
        "_meta": {"hostvars": {}},
        "all": {"children": ["app", "db", "all_phase1"]},
        "app": {"hosts": []},
        "db": {"hosts": []},
        "all_phase1": {"hosts": []},
    }

    for host, attrs in hosts.items():
        ip = attrs.get("ip")
        if not ip:
            continue
        inventory["_meta"]["hostvars"][host] = {"ansible_host": ip}
        inventory["all_phase1"]["hosts"].append(host)
        if host in ("app-staging", "app-prod"):
            inventory["app"]["hosts"].append(host)
        if host == "db-prod":
            inventory["db"]["hosts"].append(host)

    return inventory


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--list":
        print(json.dumps(build_inventory()))
    elif len(sys.argv) == 3 and sys.argv[1] == "--host":
        print(json.dumps({}))
    else:
        print(json.dumps(build_inventory()))
