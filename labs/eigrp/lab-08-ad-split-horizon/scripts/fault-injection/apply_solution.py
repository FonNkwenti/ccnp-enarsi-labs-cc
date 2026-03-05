#!/usr/bin/env python3
"""
apply_solution.py — EIGRP Lab 08: Administrative Distance & Split Horizon

Restores all active devices to the known-good solution state (solutions/).
Run this after each troubleshooting ticket to reset before the next scenario.
"""

import os
from netmiko import ConnectHandler

CONSOLE_HOST = "127.0.0.1"
SOLUTIONS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "solutions")

DEVICES = [
    {"name": "R1", "port": 5001, "cfg": "R1.cfg"},
    {"name": "R2", "port": 5002, "cfg": "R2.cfg"},
    {"name": "R3", "port": 5003, "cfg": "R3.cfg"},
    {"name": "R4", "port": 5004, "cfg": "R4.cfg"},
]


def restore_device(device):
    cfg_path = os.path.join(SOLUTIONS_DIR, device["cfg"])
    with open(cfg_path) as f:
        commands = [
            line.rstrip()
            for line in f
            if line.strip() and not line.strip().startswith("!")
        ]

    dev = {
        "device_type": "cisco_ios_telnet",
        "host": CONSOLE_HOST,
        "port": device["port"],
        "username": "",
        "password": "",
        "secret": "",
        "timeout": 30,
    }

    print(f"[*] Restoring {device['name']} on port {device['port']}...")
    try:
        conn = ConnectHandler(**dev)
        conn.send_config_set(commands)
        conn.disconnect()
        print(f"[+] {device['name']} restored.")
    except Exception as e:
        print(f"[!] {device['name']} failed: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("Restoring Lab 08 to Known-Good Solution State")
    print("=" * 60)
    for device in DEVICES:
        restore_device(device)
    print("\n[+] All devices restored. Ready for next scenario.")
