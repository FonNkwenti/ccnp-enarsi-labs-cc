#!/usr/bin/env python3
"""
Lab 06 — Ticket 2 Fault Injection
Changes R4's stub type from 'connected summary' to 'receive-only'.
A receive-only stub router maintains its EIGRP adjacency but suppresses
all outbound route advertisements — R4 will not announce any prefixes,
making 192.168.4.0/24 and R4's loopbacks unreachable from the rest of the domain.

Fault: R4 IPv4/IPv6 AF -> eigrp stub receive-only
  - R1-R4 adjacency remains UP (Hellos continue)
  - R4 sends zero prefix advertisements
  - 192.168.4.0/24 disappears from R1, R2, R3 routing tables

Usage: python3 inject_scenario_02.py
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
    "eigrp stub receive-only",
    "exit-address-family",
    "address-family ipv6 unicast autonomous-system 100",
    "eigrp stub receive-only",
    "exit-address-family",
]

if __name__ == "__main__":
    print("[*] Injecting Ticket 2 fault: eigrp stub receive-only on R4...")
    try:
        with ConnectHandler(**R4) as conn:
            conn.enable()
            conn.send_config_set(FAULT_COMMANDS)
            print("[+] Fault injected on R4.")
    except Exception as e:
        print(f"[!] Error: {e}")
    print("[*] Wait ~10 s for topology to update, then check:")
    print("    R1# show ip eigrp neighbors")
    print("    Expected: R4 still present (adjacency up)")
    print("    R1# show ip route 192.168.4.0")
    print("    Expected: Network not in table (R4 advertising nothing)")
    print("    R1# show ip eigrp neighbors detail")
    print("    Expected: Stub Peer Advertising (RECEIVE-ONLY) Routes")
