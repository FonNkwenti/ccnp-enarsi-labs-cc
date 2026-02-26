#!/usr/bin/env python3
"""
Lab 03 — Ticket 3 fault injector.
Injects an incomplete K-value restore on R2 — sets K4=1 (non-default).
This leaves R2 with K-values that don't match R1 or R3, causing adjacency
loss and inconsistent metrics. Simulates a partially reverted change.
"""

from netmiko import ConnectHandler

device = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5002,   # R2
    "username": "",
    "password": "",
    "secret": "",
    "global_delay_factor": 2,
}

fault_commands = [
    "router eigrp ENARSI",
    " address-family ipv4 unicast autonomous-system 100",
    "  metric weights 0 1 0 1 1 0",
    "  exit-address-family",
]


def inject():
    print("[*] Injecting Ticket 3 fault: incomplete K-value restore on R2 (K4=1)...")
    with ConnectHandler(**device) as conn:
        conn.enable()
        output = conn.send_config_set(fault_commands)
        print(output)
    print("[+] Fault injected. R2 K-values now differ from R1 and R3.")
    print("    Symptom: R2 loses EIGRP adjacency; route to 10.0.0.1/32 missing or degraded.")


if __name__ == "__main__":
    inject()
