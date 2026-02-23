#!/usr/bin/env python3
"""
apply_solution.py — EIGRP Lab 01: Classic Mode Adjacency

Restores all devices to the correct solution configuration.
Run this after any fault injection scenario to reset the lab.

Usage:
  python3 apply_solution.py
"""

import sys
import time
from pathlib import Path
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException

LAB_DIR = Path(__file__).parent.parent.parent
SOLUTIONS_DIR = LAB_DIR / "solutions"

DEVICES = [
    {"name": "R1", "console_port": 5001},
    {"name": "R2", "console_port": 5002},
    {"name": "R3", "console_port": 5003},
]


def restore_device(device_info: dict) -> bool:
    name = device_info["name"]
    port = device_info["console_port"]
    cfg_file = SOLUTIONS_DIR / f"{name}.cfg"

    if not cfg_file.exists():
        print(f"  [!] Solution file not found: {cfg_file}")
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
        print(f"  [+] Connected. Restoring solution config...")
        conn.send_config_set(config_lines)
        conn.save_config()
        conn.disconnect()
        print(f"  [+] {name}: restored.\n")
        return True
    except NetmikoTimeoutException:
        print(f"  [!] {name}: connection timed out.\n")
        return False
    except Exception as e:
        print(f"  [!] {name}: error — {e}\n")
        return False


def main():
    print("=" * 60)
    print("  EIGRP Lab 01 — Restoring Solution Configuration")
    print("=" * 60)
    print()

    results = []
    for device in DEVICES:
        results.append(restore_device(device))
        time.sleep(1)

    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"  Restore complete: {passed}/{total} devices restored.")
    if passed < total:
        print("  [!] Some devices failed. Check GNS3 and retry.")
        sys.exit(1)
    print("  All devices back to correct EIGRP configuration.")
    print("=" * 60)


if __name__ == "__main__":
    main()
