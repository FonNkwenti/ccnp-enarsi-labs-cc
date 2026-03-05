#!/usr/bin/env python3
"""
Fault Injection Script — Ticket 2

Injects:    EIGRP AD set to 255 on R2, causing all EIGRP routes to be dropped from the RIB
Target:     R2
"""

from netmiko import ConnectHandler
import sys

DEVICE_NAME  = "R2"
CONSOLE_HOST = "127.0.0.1"
CONSOLE_PORT = 5002

FAULT_COMMANDS = [
    "router eigrp ENARSI",
    "address-family ipv4 unicast autonomous-system 100",
    "distance eigrp 255 255",
    "exit-address-family",
]


def inject_fault():
    print(f"[*] Connecting to {DEVICE_NAME} on port {CONSOLE_PORT}...")
    try:
        conn = ConnectHandler(
            device_type="cisco_ios_telnet",
            host=CONSOLE_HOST,
            port=CONSOLE_PORT,
            username="", password="", secret="",
            timeout=15,
        )
        print(f"[+] Connected. Injecting fault...")
        conn.send_config_set(FAULT_COMMANDS)
        conn.disconnect()
        print(f"[+] Fault injected on {DEVICE_NAME}.")
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 50)
    print("Fault Injection: Ticket 2")
    print("=" * 50)
    inject_fault()
