#!/usr/bin/env python3
"""
Lab 01 — Apply Solution
Restores correct EIGRP classic mode configuration on all routers.
Run after any fault-injection scenario to return the lab to a working state.

Usage: python3 apply_solution.py
"""

from netmiko import ConnectHandler

DEVICES = [
    {
        "device_type": "cisco_ios_telnet",
        "host": "127.0.0.1",
        "port": 5001,
        "username": "",
        "password": "",
        "global_delay_factor": 2,
        "name": "R1",
    },
    {
        "device_type": "cisco_ios_telnet",
        "host": "127.0.0.1",
        "port": 5002,
        "username": "",
        "password": "",
        "global_delay_factor": 2,
        "name": "R2",
    },
    {
        "device_type": "cisco_ios_telnet",
        "host": "127.0.0.1",
        "port": 5003,
        "username": "",
        "password": "",
        "global_delay_factor": 2,
        "name": "R3",
    },
]

# Idempotent: remove any incorrect EIGRP process first, then apply correct config
SOLUTIONS = {
    "R1": [
        "no router eigrp 100",
        "router eigrp 100",
        " eigrp log-neighbor-changes",
        " network 10.12.0.0 0.0.0.3",
        " network 10.13.0.0 0.0.0.3",
        " network 10.0.0.1 0.0.0.0",
        " no auto-summary",
        " no passive-interface FastEthernet0/0",
    ],
    "R2": [
        "no router eigrp 200",
        "no router eigrp 100",
        "router eigrp 100",
        " eigrp log-neighbor-changes",
        " network 10.12.0.0 0.0.0.3",
        " network 10.23.0.0 0.0.0.3",
        " network 10.0.0.2 0.0.0.0",
        " no auto-summary",
    ],
    "R3": [
        "router eigrp 100",
        " eigrp log-neighbor-changes",
        " network 10.13.0.0 0.0.0.3",
        " network 10.23.0.0 0.0.0.3",
        " network 10.0.0.3 0.0.0.0",
        " no auto-summary",
    ],
}


def restore(device_info):
    device = {k: v for k, v in device_info.items() if k != "name"}
    name = device_info["name"]
    print(f"[*] Restoring {name}...")
    try:
        with ConnectHandler(**device) as conn:
            conn.enable()
            conn.send_config_set(SOLUTIONS[name])
            print(f"[+] {name} restored.")
    except Exception as e:
        print(f"[!] Error restoring {name}: {e}")


if __name__ == "__main__":
    print("Lab 01 -- Applying solution configs (restoring correct EIGRP state)")
    print("=" * 60)
    for d in DEVICES:
        restore(d)
    print("=" * 60)
    print("[*] All routers restored.")
    print("[*] Verify with: show ip eigrp neighbors (on all routers)")
