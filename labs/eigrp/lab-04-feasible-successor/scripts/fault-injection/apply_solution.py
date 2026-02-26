#!/usr/bin/env python3
"""
Lab 04 — Restore Known-Good State
Pushes the Lab 04 solution configs to all routers, undoing any injected faults
and restoring the correct EIGRP topology table, Feasible Successor, and UCAL.

Usage: python3 apply_solution.py

Restores:
  - R1: variance 5 under IPv4 AF; fa0/0 bandwidth 512 / delay 2000 intact
  - R2: Lo0 delay cleared (back to default 5000)
  - R3: fa0/1 delay cleared (back to default 100)
"""

import os
from netmiko import ConnectHandler

ROUTERS = [
    {"device_type": "cisco_ios_telnet", "host": "127.0.0.1", "port": 5001,
     "username": "", "password": "", "secret": "", "global_delay_factor": 2, "name": "R1"},
    {"device_type": "cisco_ios_telnet", "host": "127.0.0.1", "port": 5002,
     "username": "", "password": "", "secret": "", "global_delay_factor": 2, "name": "R2"},
    {"device_type": "cisco_ios_telnet", "host": "127.0.0.1", "port": 5003,
     "username": "", "password": "", "secret": "", "global_delay_factor": 2, "name": "R3"},
]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOLUTIONS_DIR = os.path.join(SCRIPT_DIR, "..", "..", "solutions")


def load_solution(device_name):
    cfg_path = os.path.join(SOLUTIONS_DIR, f"{device_name}.cfg")
    with open(os.path.normpath(cfg_path)) as f:
        lines = [
            line.rstrip()
            for line in f
            if line.strip() and not line.strip().startswith("!")
        ]
    return lines


def push_solution(router_info):
    device = {k: v for k, v in router_info.items() if k != "name"}
    name = router_info["name"]
    commands = load_solution(name)
    print(f"[*] Restoring {name}...")
    try:
        with ConnectHandler(**device) as conn:
            conn.enable()
            conn.send_config_set(commands)
            print(f"[+] {name} restored.")
    except Exception as e:
        print(f"[!] Error restoring {name}: {e}")


if __name__ == "__main__":
    print("Lab 04 — Restoring solution state (all faults cleared)")
    print("=" * 60)
    for router in ROUTERS:
        push_solution(router)
    print("=" * 60)
    print("[*] Done. Verify:")
    print("    R1# show ip eigrp topology 10.0.0.2 255.255.255.255")
    print("    Expected: Feasible Successor via R2 restored; FC met")
    print("    R1# show ip route 10.0.0.2")
    print("    Expected: two EIGRP paths (UCAL active, variance 5)")
