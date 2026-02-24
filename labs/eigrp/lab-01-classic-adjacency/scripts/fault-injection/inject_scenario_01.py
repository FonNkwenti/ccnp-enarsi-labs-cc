#!/usr/bin/env python3
"""
Lab 01 — Ticket 09-1: Branch A Is Completely Isolated
Fault: R2 is configured with EIGRP AS 200 instead of AS 100.
Symptom: R2 has no EIGRP neighbors; R1 and R3 adjacency with each other is unaffected.
"""

from netmiko import ConnectHandler

R2 = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5002,
    "username": "",
    "password": "",
    "global_delay_factor": 2,
}

# Remove correct AS, configure wrong AS with same network statements
FAULT_COMMANDS = [
    "no router eigrp 100",
    "router eigrp 200",
    " network 10.12.0.0 0.0.0.3",
    " network 10.23.0.0 0.0.0.3",
    " network 10.0.0.2 0.0.0.0",
    " no auto-summary",
]


def inject():
    print("[*] Injecting Scenario 01: EIGRP AS Mismatch on R2 (200 instead of 100)...")
    try:
        with ConnectHandler(**R2) as conn:
            conn.enable()
            conn.send_config_set(FAULT_COMMANDS)
            print("[+] Fault injected on R2.")
            print("[*] Diagnose with: show ip eigrp neighbors (on R1, R2, R3)")
    except Exception as e:
        print(f"[!] Error: {e}")


if __name__ == "__main__":
    inject()
