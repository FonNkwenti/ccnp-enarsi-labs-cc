#!/usr/bin/env python3
"""
Fault Injection Script: Passive Interface

Injects:    Sets FastEthernet0/0 as passive on R1,
            blocking EIGRP Hello packets on the R1-R2 link.
Target:     R1
Fault Type: Passive Interface (1.9.b)

Symptom:    R1-R2 EIGRP adjacency drops (R2 shows 0 neighbors via R1).
            R2 can no longer reach R3 via R1.
            R3 can still reach R2 directly (R2-R3 link unaffected).

Student task: Identify which interface is passive and remove the restriction.
"""

from netmiko import ConnectHandler
import sys

DEVICE_NAME  = "R1"
CONSOLE_HOST = "127.0.0.1"
CONSOLE_PORT = 5001

FAULT_COMMANDS = [
    "router eigrp 100",
    "passive-interface FastEthernet0/0",
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
    print("Fault Injection: Passive Interface Fa0/0 on R1")
    print("=" * 50)
    inject_fault()
