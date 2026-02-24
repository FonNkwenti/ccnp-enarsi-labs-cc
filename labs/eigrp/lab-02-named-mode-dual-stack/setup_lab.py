"""
Lab 02 — EIGRP Named Mode & Dual-Stack IPv6 Address Family
Setup script: pushes initial-configs to R1, R2, R3 via GNS3 console (Netmiko telnet).

Usage:
    python setup_lab.py

Requirements:
    pip install netmiko
    GNS3 project running with R1/R2/R3 consoles on 127.0.0.1:5001-5003
"""

import os
from netmiko import ConnectHandler

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INITIAL_CONFIGS = os.path.join(SCRIPT_DIR, "initial-configs")

devices = [
    {"name": "R1", "host": "127.0.0.1", "port": 5001, "cfg": "R1.cfg"},
    {"name": "R2", "host": "127.0.0.1", "port": 5002, "cfg": "R2.cfg"},
    {"name": "R3", "host": "127.0.0.1", "port": 5003, "cfg": "R3.cfg"},
]


def push_config(device):
    cfg_path = os.path.join(INITIAL_CONFIGS, device["cfg"])
    with open(cfg_path) as f:
        # Strip comment lines and blank lines; keep IOS commands only
        commands = [
            line.rstrip()
            for line in f
            if line.strip() and not line.strip().startswith("!")
        ]

    conn_params = {
        "device_type": "cisco_ios_telnet",
        "host": device["host"],
        "port": device["port"],
        "username": "",
        "password": "",
        "secret": "",
        "global_delay_factor": 2,
    }

    print(f"[*] Connecting to {device['name']} ({device['host']}:{device['port']})...")
    with ConnectHandler(**conn_params) as net_connect:
        net_connect.enable()
        net_connect.send_config_set(commands, cmd_verify=False)
        net_connect.send_command("write memory", expect_string=r"#")
        print(f"[+] {device['name']} — config pushed and saved.")


def main():
    print("=" * 55)
    print("Lab 02 Setup — EIGRP Named Mode & Dual-Stack")
    print("=" * 55)
    for device in devices:
        try:
            push_config(device)
        except Exception as exc:
            print(f"[!] {device['name']} failed: {exc}")
    print("\n[*] Setup complete. Verify with:")
    print("    show ip eigrp neighbors")
    print("    show ipv6 eigrp neighbors")


if __name__ == "__main__":
    main()
