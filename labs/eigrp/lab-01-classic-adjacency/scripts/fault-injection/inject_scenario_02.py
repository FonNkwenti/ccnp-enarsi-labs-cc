#!/usr/bin/env python3
"""
Lab 01 — Ticket 09-2: R1 Cannot Reach Branch A
Fault: R1 FastEthernet0/0 is set as a passive-interface under EIGRP.
Symptom: R1-R2 adjacency fails; R1 shows only R3 as a neighbor; R2 has no neighbor with R1.
"""

from netmiko import ConnectHandler

R1 = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5001,
    "username": "",
    "password": "",
    "global_delay_factor": 2,
}

FAULT_COMMANDS = [
    "router eigrp 100",
    " passive-interface FastEthernet0/0",
]


def inject():
    print("[*] Injecting Scenario 02: passive-interface fa0/0 on R1...")
    try:
        with ConnectHandler(**R1) as conn:
            conn.enable()
            conn.send_config_set(FAULT_COMMANDS)
            print("[+] Fault injected on R1.")
            print("[*] Diagnose with: show ip eigrp neighbors (on R1 and R2)")
    except Exception as e:
        print(f"[!] Error: {e}")


if __name__ == "__main__":
    inject()
