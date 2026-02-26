#!/usr/bin/env python3
"""
Lab 03 — Ticket 1 fault injector.
Injects a K-value mismatch on R1 by setting K2=1.
This causes both R2 and R3 to drop their EIGRP adjacency with R1.
"""

from netmiko import ConnectHandler

device = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5001,   # R1
    "username": "",
    "password": "",
    "secret": "",
    "global_delay_factor": 2,
}

fault_commands = [
    "router eigrp ENARSI",
    " address-family ipv4 unicast autonomous-system 100",
    "  metric weights 0 1 1 1 0 0",
    "  exit-address-family",
]


def inject():
    print("[*] Injecting Ticket 1 fault: K-value mismatch on R1 (K2=1)...")
    with ConnectHandler(**device) as conn:
        conn.enable()
        output = conn.send_config_set(fault_commands)
        print(output)
    print("[+] Fault injected. R2 and R3 should drop adjacency with R1.")
    print("    Symptom: 'show ip eigrp neighbors' on R2/R3 shows no neighbors.")


if __name__ == "__main__":
    inject()
