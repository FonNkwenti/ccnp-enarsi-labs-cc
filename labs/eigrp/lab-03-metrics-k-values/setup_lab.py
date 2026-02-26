#!/usr/bin/env python3
"""
Lab 03 -- EIGRP Metrics: Bandwidth, Delay & K-Values
Setup script: Pushes initial-configs to all routers via GNS3 console (Telnet).

Usage: python3 setup_lab.py

Prerequisites:
  - GNS3 running with R1, R2, R3 all started
  - pip install netmiko
"""

import os
from netmiko import ConnectHandler

ROUTERS = [
    {
        "device_type": "cisco_ios_telnet",
        "host": "127.0.0.1",
        "port": 5001,
        "username": "",
        "password": "",
        "secret": "",
        "global_delay_factor": 2,
        "name": "R1",
    },
    {
        "device_type": "cisco_ios_telnet",
        "host": "127.0.0.1",
        "port": 5002,
        "username": "",
        "password": "",
        "secret": "",
        "global_delay_factor": 2,
        "name": "R2",
    },
    {
        "device_type": "cisco_ios_telnet",
        "host": "127.0.0.1",
        "port": 5003,
        "username": "",
        "password": "",
        "secret": "",
        "global_delay_factor": 2,
        "name": "R3",
    },
]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_config(device_name):
    cfg_path = os.path.join(SCRIPT_DIR, "initial-configs", f"{device_name}.cfg")
    with open(cfg_path) as f:
        # Strip comment lines and blank lines; return as a list of commands
        lines = [
            line.rstrip()
            for line in f
            if line.strip() and not line.strip().startswith("!")
        ]
    return lines


def push_config(router_info):
    device = {k: v for k, v in router_info.items() if k != "name"}
    name = router_info["name"]
    commands = load_config(name)
    print(f"[*] Connecting to {name} on port {device['port']}...")
    try:
        with ConnectHandler(**device) as conn:
            conn.enable()
            conn.send_config_set(commands)
            print(f"[+] {name} configured successfully.")
    except Exception as e:
        print(f"[!] Error configuring {name}: {e}")


if __name__ == "__main__":
    print("Lab 03 Setup -- Pushing initial-configs (Named Mode EIGRP, default metrics)")
    print("=" * 65)
    for router in ROUTERS:
        push_config(router)
    print("=" * 65)
    print("[*] Done. Verify adjacencies: show ip eigrp neighbors")
    print("[*] Check default metrics: show ip eigrp topology")
    print("[*] Now work through the lab challenge per workbook.md")
