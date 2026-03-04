#!/usr/bin/env python3
"""
Lab 07 — Route Filtering & Route Maps
Setup script: Pushes initial-configs to R1, R2, R3, R4 via GNS3 console (Telnet).

Usage: python3 setup_lab.py

Prerequisites:
  - GNS3 running with R1, R2, R3, R4 all started
  - pip install netmiko
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

CONFIG_DIR = pathlib.Path(__file__).parent / "initial-configs"


def push_config(router_info):
    name = router_info["name"]
    device = {k: v for k, v in router_info.items() if k != "name"}
    cfg_path = CONFIG_DIR / f"{name}.cfg"
    commands = [line.rstrip() for line in cfg_path.read_text().splitlines()
                if line.strip() and not line.strip().startswith("!")]
    print(f"[*] Connecting to {name} on port {device['port']}...")
    try:
        with ConnectHandler(**device) as conn:
            conn.enable()
            conn.send_config_set(commands)
            print(f"[+] {name} configured successfully.")
    except Exception as e:
        print(f"[!] Error configuring {name}: {e}")


if __name__ == "__main__":
    print("Lab 07 Setup — Pushing initial-configs (lab-06 solutions: full EIGRP Named Mode + stub)")
    print("=" * 70)
    for router in ROUTERS:
        push_config(router)
    print("=" * 70)
    print("[*] Done. All routers loaded with lab-06 solutions as starting point.")
    print("[*] Verify baseline with: show ip eigrp neighbors / show ip route")
    print("[*] Then configure: prefix-lists, route-maps, and distribute-lists per workbook.")
