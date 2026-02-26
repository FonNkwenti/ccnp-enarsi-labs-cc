#!/usr/bin/env python3
"""
Lab 04 — Ticket 2 Fault Injection
Disables unequal-cost load balancing on R1 by resetting variance to 1 (default).
With variance 1, only the best-metric path (via R3) is installed in the routing
table, and the Feasible Successor via R2 fa0/0 is not forwarded.

Fault: R1 EIGRP IPv4 AF variance set to 1 (removes UCAL)

Usage: python3 inject_scenario_02.py
"""

from netmiko import ConnectHandler

R1 = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5001,
    "username": "",
    "password": "",
    "secret": "",
    "global_delay_factor": 2,
}

FAULT_COMMANDS = [
    "router eigrp ENARSI",
    "address-family ipv4 unicast autonomous-system 100",
    "variance 1",
    "exit-address-family",
]

if __name__ == "__main__":
    print("[*] Injecting Ticket 2 fault: resetting R1 variance to 1 (disabling UCAL)...")
    try:
        with ConnectHandler(**R1) as conn:
            conn.enable()
            conn.send_config_set(FAULT_COMMANDS)
            print("[+] Fault injected on R1.")
    except Exception as e:
        print(f"[!] Error: {e}")
    print("[*] Check immediately:")
    print("    R1# show ip route 10.0.0.2")
    print("    Expected: only ONE EIGRP entry (via R3) — direct R2 path missing")
    print("    R1# show running-config | section address-family ipv4")
    print("    Expected: 'variance 1' or no variance command")
