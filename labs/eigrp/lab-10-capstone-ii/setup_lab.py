#!/usr/bin/env python3
"""Lab 10 Setup: Load initial-configs and verify connectivity."""
from netmiko import ConnectHandler
import sys
import time

ROUTERS = [
    {"host": "localhost", "port": 5001, "device_type": "cisco_ios_telnet", "username": "", "password": "", "secret": "", "name": "R1"},
    {"host": "localhost", "port": 5002, "device_type": "cisco_ios_telnet", "username": "", "password": "", "secret": "", "name": "R2"},
    {"host": "localhost", "port": 5003, "device_type": "cisco_ios_telnet", "username": "", "password": "", "secret": "", "name": "R3"},
]

if 10 >= 6:
    ROUTERS.append({"host": "localhost", "port": 5004, "device_type": "cisco_ios_telnet", "username": "", "password": "", "secret": "", "name": "R4"})

CONFIG_DIR = "initial-configs"

def load_config(router_info):
    try:
        net_connect = ConnectHandler(**router_info)
        router_name = router_info["name"]
        config_file = f"{CONFIG_DIR}/{router_name}.cfg"
        print(f"[*] Loading {router_name} config...")
        with open(config_file, "r") as f:
            commands = f.read().split("\\n")
            commands = [cmd.strip() for cmd in commands if cmd.strip() and not cmd.startswith("!")]
            net_connect.send_config_set(commands)
        net_connect.disconnect()
        print(f"[+] {router_name} configured\\n")
        return True
    except Exception as e:
        print(f"[-] Error configuring {router_name}: {e}\\n")
        return False

if __name__ == "__main__":
    print("\\n=== Lab 10 Setup ===\\n")
    success_count = sum(load_config(r) for r in ROUTERS)
    print(f"[+] Configured {success_count}/{len(ROUTERS)} routers\\n")
    sys.exit(0 if success_count == len(ROUTERS) else 1)
