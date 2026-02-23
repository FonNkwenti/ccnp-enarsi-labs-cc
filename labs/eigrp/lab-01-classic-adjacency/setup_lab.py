#!/usr/bin/env python3
"""
setup_lab.py — EIGRP Lab 01: Classic Mode Adjacency

Pushes initial-configs/ to each router via GNS3 console ports (Netmiko telnet).
Run this script BEFORE starting the lab challenge.

Prerequisites:
  pip install netmiko
  GNS3 lab topology running with all routers powered on
"""

import sys
import time
from pathlib import Path
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

LAB_DIR = Path(__file__).parent
INITIAL_CONFIGS = LAB_DIR / "initial-configs"

DEVICES = [
    {"name": "R1", "console_port": 5001},
    {"name": "R2", "console_port": 5002},
    {"name": "R3", "console_port": 5003},
]


def push_config(device_info: dict) -> bool:
    name = device_info["name"]
    port = device_info["console_port"]
    cfg_file = INITIAL_CONFIGS / f"{name}.cfg"

    if not cfg_file.exists():
        print(f"  [!] Config file not found: {cfg_file}")
        return False

    config_lines = [
        line.strip()
        for line in cfg_file.read_text().splitlines()
        if line.strip() and not line.strip().startswith("!")
    ]

    device = {
        "device_type": "cisco_ios_telnet",
        "host": "127.0.0.1",
        "port": port,
        "username": "",
        "password": "",
        "secret": "",
        "timeout": 15,
        "global_delay_factor": 2,
    }

    try:
        print(f"  [*] Connecting to {name} on port {port}...")
        conn = ConnectHandler(**device)
        conn.enable()
        print(f"  [+] Connected. Pushing initial config...")
        conn.send_config_set(config_lines)
        conn.save_config()
        conn.disconnect()
        print(f"  [+] {name}: config applied and saved.\n")
        return True
    except NetmikoTimeoutException:
        print(f"  [!] {name}: connection timed out. Is the router powered on in GNS3?\n")
        return False
    except Exception as e:
        print(f"  [!] {name}: error — {e}\n")
        return False


def main():
    print("=" * 60)
    print("  EIGRP Lab 01 — Setup: Pushing Initial Configurations")
    print("=" * 60)
    print()

    results = []
    for device in DEVICES:
        results.append(push_config(device))
        time.sleep(1)

    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"  Setup complete: {passed}/{total} devices configured successfully.")
    if passed < total:
        print("  [!] Some devices failed. Check GNS3 topology and retry.")
        sys.exit(1)
    print("  Ready to start the lab challenge.")
    print("=" * 60)


if __name__ == "__main__":
    main()
