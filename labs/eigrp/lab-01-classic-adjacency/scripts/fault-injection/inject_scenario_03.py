#!/usr/bin/env python3
"""
Fault Injection Script: Missing Network Statement

Injects:    Removes the network statement for 10.23.0.0/30 from R3,
            causing R3's Fa0/1 subnet to stop being advertised via EIGRP.
Target:     R3
Fault Type: Missing network statement (1.9.b)

Symptom:    R3's FastEthernet0/1 interface (10.23.0.0/30) is no longer
            in the EIGRP routing table on R1 or R2.
            R2's Fa0/1 interface loses its EIGRP peer with R3 (adjacency
            drops because R3 is not sending Hellos on that interface).
            Pings from R1 to 10.23.0.2 fail.

Student task: Identify the missing network statement and restore full EIGRP
              advertisement of all connected subnets on R3.
"""

from netmiko import ConnectHandler
import sys

DEVICE_NAME  = "R3"
CONSOLE_HOST = "127.0.0.1"
CONSOLE_PORT = 5003

FAULT_COMMANDS = [
    "router eigrp 100",
    "no network 10.23.0.0 0.0.0.3",
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
    print("Fault Injection: Missing network Statement on R3")
    print("=" * 50)
    inject_fault()
