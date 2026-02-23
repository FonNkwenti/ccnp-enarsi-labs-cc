#!/usr/bin/env python3
"""
Fault Injection Script: AS Number Mismatch

Injects:    Replaces EIGRP AS 100 with AS 200 on R2,
            causing R2 to lose all EIGRP neighbors.
Target:     R2
Fault Type: AS Number Mismatch (1.9.b)

Symptom:    R2 shows no EIGRP neighbors.
            R1 and R3 lose the 10.0.0.2/32 and 10.23.0.0/30 routes.
            Pings from R1 to R2 Lo0 (10.0.0.2) fail.

Student task: Identify why R2 has no EIGRP neighbors and restore adjacency.
"""

from netmiko import ConnectHandler
import sys

DEVICE_NAME  = "R2"
CONSOLE_HOST = "127.0.0.1"
CONSOLE_PORT = 5002

FAULT_COMMANDS = [
    "no router eigrp 100",
    "router eigrp 200",
    "network 10.0.0.2 0.0.0.0",
    "network 10.12.0.0 0.0.0.3",
    "network 10.23.0.0 0.0.0.3",
    "no auto-summary",
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
    print("Fault Injection: AS Number Mismatch on R2")
    print("=" * 50)
    inject_fault()
