#!/usr/bin/env python3
"""
Lab 07 — Apply Solution (Restore Known-Good State)
Restores all four routers to the lab-07 solution configuration.
Run this after each troubleshooting ticket to reset for the next scenario.

Usage: python3 apply_solution.py
"""

import pathlib
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

SOLUTIONS_DIR = pathlib.Path(__file__).parent.parent.parent / "solutions"


def restore(router_info):
    name = router_info["name"]
    device = {k: v for k, v in router_info.items() if k != "name"}
    cfg_path = SOLUTIONS_DIR / f"{name}.cfg"
    commands = [line.rstrip() for line in cfg_path.read_text().splitlines()
                if line.strip() and not line.strip().startswith("!")]
    print(f"[*] Restoring {name}...")
    try:
        with ConnectHandler(**device) as conn:
            conn.enable()
            conn.send_config_set(commands)
            print(f"[+] {name} restored.")
    except Exception as e:
        print(f"[!] Error restoring {name}: {e}")


if __name__ == "__main__":
    print("Lab 07 — Restoring solution configuration on all routers")
    print("=" * 60)
    for router in ROUTERS:
        restore(router)
    print("=" * 60)
    print("[*] All routers restored. Verify with:")
    print("    R2# show ip route 192.168.4.0  (should be absent)")
    print("    R4# show ip route 172.16.20.0  (should be absent)")
    print("    R1# show ip eigrp topology 172.16.20.0/23  (Tag: 200)")
