#!/usr/bin/env python3
"""
inject_scenario_03.py

Injects: Remove summary-address 172.16.30.0 255.255.254.0 from R3's
         af-interface FastEthernet0/1 block, causing individual /24
         prefixes to leak to R2 via the direct R2-R3 link while R1
         continues to receive the correct /23 summary via Fa0/0.
Target:  R3
"""

import sys
from netmiko import ConnectHandler

DEVICE_NAME  = "R3"
CONSOLE_HOST = "127.0.0.1"
CONSOLE_PORT = 5003

FAULT_COMMANDS = [
    "router eigrp ENARSI",
    "address-family ipv4 unicast autonomous-system 100",
    "af-interface FastEthernet0/1",
    "no summary-address 172.16.30.0 255.255.254.0",
    "exit-af-interface",
    "exit-address-family",
]


def inject_fault():
    device = {
        "device_type": "cisco_ios_telnet",
        "host": CONSOLE_HOST,
        "port": CONSOLE_PORT,
        "username": "",
        "password": "",
        "secret": "",
        "timeout": 10,
    }
    print(f"[*] Connecting to {DEVICE_NAME} on {CONSOLE_HOST}:{CONSOLE_PORT}...")
    try:
        with ConnectHandler(**device) as conn:
            conn.enable()
            print(f"[+] Connected. Injecting fault on {DEVICE_NAME}...")
            conn.send_config_set(FAULT_COMMANDS)
            print(f"[+] Fault injected on {DEVICE_NAME}.")
            print()
            print("Verification hints:")
            print("  R2# show ip route eigrp | include 172.16.3")
            print("  R1# show ip route eigrp | include 172.16.3")
            print("  R3# show run | section router eigrp")
            print("  (Expect /24 specifics on R2, /23 summary still on R1)")
    except Exception as e:
        print(f"[!] Error connecting to {DEVICE_NAME}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 55)
    print("Fault Injection: Lab 05 — Ticket 3")
    print("=" * 55)
    inject_fault()
