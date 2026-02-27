#!/usr/bin/env python3
"""
apply_solution.py

Restores all devices in Lab 05 (EIGRP Summarization) to the solution
state by pushing solutions/<Device>.cfg to each router via Netmiko.
"""

import os
import sys
from netmiko import ConnectHandler

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
LAB_ROOT     = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
SOLUTIONS_DIR = os.path.join(LAB_ROOT, "solutions")

ROUTERS = [
    {"name": "R1", "host": "127.0.0.1", "port": 5001},
    {"name": "R2", "host": "127.0.0.1", "port": 5002},
    {"name": "R3", "host": "127.0.0.1", "port": 5003},
]


def load_solution(device_name):
    cfg_path = os.path.join(SOLUTIONS_DIR, f"{device_name}.cfg")
    if not os.path.isfile(cfg_path):
        print(f"[!] Solution file not found: {cfg_path}")
        sys.exit(1)
    lines = []
    with open(cfg_path) as f:
        for line in f:
            stripped = line.rstrip()
            if stripped and not stripped.startswith("!"):
                lines.append(stripped)
    return lines


def push_solution(router_info):
    name = router_info["name"]
    device = {
        "device_type": "cisco_ios_telnet",
        "host": router_info["host"],
        "port": router_info["port"],
        "username": "",
        "password": "",
        "secret": "",
        "timeout": 15,
    }
    print(f"[*] Connecting to {name} on {router_info['host']}:{router_info['port']}...")
    try:
        commands = load_solution(name)
        with ConnectHandler(**device) as conn:
            conn.enable()
            conn.send_config_set(commands)
            print(f"[+] {name} — solution applied ({len(commands)} commands).")
    except Exception as e:
        print(f"[!] Error restoring {name}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 55)
    print("=== Restoring Lab 05 to Solution State ===")
    print("=" * 55)
    for router in ROUTERS:
        push_solution(router)
    print()
    print("All devices restored. Verify with:")
    print("  R1# show ip route eigrp")
    print("  R1# show ip route | include Null0")
    print("  R2# show ip route | include Null0")
    print("  R3# show ip route | include Null0")
    print("  R1# ping 172.16.30.1 source loopback0")
    print("  R1# ping 172.16.31.1 source loopback0")
    print("=" * 55)
