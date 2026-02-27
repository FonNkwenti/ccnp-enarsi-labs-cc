#!/usr/bin/env python3
"""
Lab 06 — Ticket 3 Fault Injection
Removes the EIGRP network statement for R4's stub LAN (192.168.4.0/24).
The R1-R4 adjacency remains fully operational, and R4 still advertises
its router-ID prefix (10.0.0.4/32) and link subnet (10.14.0.0/30).
Only the stub LAN prefix is suppressed, making 192.168.4.0/24 unreachable.

Fault: R4 IPv4 AF -> no network 192.168.4.0 0.0.0.255
  - R1-R4 adjacency remains UP
  - 192.168.4.0/24 disappears from all routing tables
  - 10.0.0.4/32 and 10.14.0.0/30 remain in the EIGRP domain

Usage: python3 inject_scenario_03.py
"""

from netmiko import ConnectHandler

R4 = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5004,
    "username": "",
    "password": "",
    "secret": "",
    "global_delay_factor": 2,
}

FAULT_COMMANDS = [
    "router eigrp ENARSI",
    "address-family ipv4 unicast autonomous-system 100",
    "no network 192.168.4.0 0.0.0.255",
    "exit-address-family",
]

if __name__ == "__main__":
    print("[*] Injecting Ticket 3 fault: removing 192.168.4.0/24 network statement on R4...")
    try:
        with ConnectHandler(**R4) as conn:
            conn.enable()
            conn.send_config_set(FAULT_COMMANDS)
            print("[+] Fault injected on R4.")
    except Exception as e:
        print(f"[!] Error: {e}")
    print("[*] Wait ~10 s for the topology update to propagate, then check:")
    print("    R1# show ip eigrp neighbors")
    print("    Expected: R4 still present (adjacency is fine)")
    print("    R1# show ip route 192.168.4.0")
    print("    Expected: Network not in table")
    print("    R4# show ip eigrp topology")
    print("    Expected: 192.168.4.0/24 absent from R4's topology table")
