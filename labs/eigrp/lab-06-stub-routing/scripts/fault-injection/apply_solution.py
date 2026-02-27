#!/usr/bin/env python3
"""
Lab 06 — Restore Known-Good State
Pushes the Lab 06 solution configs to all four routers, undoing any injected
faults and restoring the correct EIGRP stub topology.

Usage: python3 apply_solution.py

Restores:
  - R1: network 10.14.0.0 0.0.0.3 present in IPv4 AF
  - R2: unchanged from lab-05 solutions
  - R3: unchanged from lab-05 solutions
  - R4: eigrp stub connected summary in both AFs; all three network statements present;
        no passive-interface on Fa0/0
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
    {"device_type": "cisco_ios_telnet", "host": "127.0.0.1", "port": 5004,
     "username": "", "password": "", "secret": "", "global_delay_factor": 2, "name": "R4"},
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
    print("Lab 06 — Restoring solution state (all faults cleared)")
    print("=" * 60)
    for router in ROUTERS:
        push_solution(router)
    print("=" * 60)
    print("[*] Done. Verify:")
    print("    R1# show ip eigrp neighbors")
    print("    Expected: R2, R3, and R4 all present")
    print("    R1# show ip eigrp neighbors detail")
    print("    Expected: R4 with 'Stub Peer Advertising (CONNECTED SUMMARY) Routes'")
    print("    R1# show ip route 192.168.4.0")
    print("    Expected: D    192.168.4.0/24 via 10.14.0.2")
