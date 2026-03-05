#!/usr/bin/env python3
"""
setup_lab.py — EIGRP Lab 08: Administrative Distance & Split Horizon

Pushes initial-configs/ to all active devices via Netmiko console telnet.
Run this script to reset all routers to the lab start state.
"""

import os
from netmiko import ConnectHandler

CONSOLE_HOST = "127.0.0.1"
CONFIG_DIR = os.path.join(os.path.dirname(__file__), "initial-configs")

DEVICES = [
    {"name": "R1", "port": 5001, "cfg": "R1.cfg"},
    {"name": "R2", "port": 5002, "cfg": "R2.cfg"},
    {"name": "R3", "port": 5003, "cfg": "R3.cfg"},
    {"name": "R4", "port": 5004, "cfg": "R4.cfg"},
]


def push_config(device):
    cfg_path = os.path.join(CONFIG_DIR, device["cfg"])
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

    print(f"[*] Connecting to {device['name']} on port {device['port']}...")
    try:
        conn = ConnectHandler(**dev)
        print(f"[+] Connected to {device['name']}. Pushing config...")
        conn.send_config_set(commands)
        conn.disconnect()
        print(f"[+] {device['name']} configured successfully.")
    except Exception as e:
        print(f"[!] {device['name']} failed: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("EIGRP Lab 08 — Setup: Administrative Distance & Split Horizon")
    print("=" * 60)
    for device in DEVICES:
        push_config(device)
    print("\n[+] All devices configured. Lab is ready.")
