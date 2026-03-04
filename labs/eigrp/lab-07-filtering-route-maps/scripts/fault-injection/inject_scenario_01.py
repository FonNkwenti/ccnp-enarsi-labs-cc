#!/usr/bin/env python3
"""
Lab 07 — Ticket 1 Fault Injection
Changes R1's distribute-list from outbound (out fa0/0) to inbound (in fa0/0),
causing R1 to filter incoming updates from R2 instead of outgoing updates to R2.

Effect:
  - R1 stops accepting routes from R2 via Fa0/0 (172.16.20.0/23, 10.0.0.2/32)
  - R3 and R4 lose reachability to Branch-A prefixes
  - 192.168.4.0/24 remains filtered toward R2 (the correct filter now in wrong direction)

Usage: python3 inject_scenario_01.py
"""

from netmiko import ConnectHandler

R1 = {
    "device_type": "cisco_ios_telnet", "host": "127.0.0.1", "port": 5001,
    "username": "", "password": "", "secret": "", "global_delay_factor": 2,
}

FAULT_COMMANDS = [
    "router eigrp ENARSI",
    "address-family ipv4 unicast autonomous-system 100",
    "topology base",
    "no distribute-list prefix PFX_DENY_R4_STUB out FastEthernet0/0",
    "distribute-list prefix PFX_DENY_R4_STUB in FastEthernet0/0",
    "exit-af-topology",
    "exit-address-family",
]

if __name__ == "__main__":
    print("[*] Injecting Ticket 1 fault: distribute-list direction reversed on R1 Fa0/0...")
    try:
        with ConnectHandler(**R1) as conn:
            conn.enable()
            conn.send_config_set(FAULT_COMMANDS)
            print("[+] Fault injected on R1.")
    except Exception as e:
        print(f"[!] Error: {e}")
    print("[*] Wait ~30 s for EIGRP to reconverge, then check:")
    print("    R1# show ip route 172.16.20.0")
    print("    Expected: Network not in table (Branch-A routes filtered from R1)")
    print("    R3# show ip route 172.16.20.0")
    print("    Expected: Network not in table (downstream effect)")
