#!/usr/bin/env python3
"""Restore all routers to known-good state (Lab 03 solutions)."""
from netmiko import ConnectHandler
import sys

ROUTERS = [
    {"host": "localhost", "port": 5001, "device_type": "cisco_ios_telnet", "username": "", "password": "", "secret": "", "name": "R1"},
    {"host": "localhost", "port": 5002, "device_type": "cisco_ios_telnet", "username": "", "password": "", "secret": "", "name": "R2"},
    {"host": "localhost", "port": 5003, "device_type": "cisco_ios_telnet", "username": "", "password": "", "secret": "", "name": "R3"},
]

CONFIG_DIR = "../../solutions"

def restore_router(router_info):
    """Load solution config to router."""
    try:
        net_connect = ConnectHandler(**router_info)
        router_name = router_info["name"]
        config_file = f"{CONFIG_DIR}/{router_name}.cfg"

        print(f"[*] Restoring {router_name} from solution...")
        with open(config_file, "r") as f:
            commands = f.read().split("\\n")
            commands = [cmd.strip() for cmd in commands if cmd.strip() and not cmd.startswith("!")]
            net_connect.send_config_set(commands)

        net_connect.disconnect()
        print(f"[+] {router_name} restored\\n")
        return True
    except Exception as e:
        print(f"[-] Error restoring {router_name}: {e}\\n")
        return False

if __name__ == "__main__":
    print("\\n=== Restoring Lab 03 to Solution State ===\\n")

    success = all(restore_router(router) for router in ROUTERS)

    if success:
        print("[+] All routers restored to solution state\\n")
        sys.exit(0)
    else:
        print("[-] Restoration incomplete\\n")
        sys.exit(1)
