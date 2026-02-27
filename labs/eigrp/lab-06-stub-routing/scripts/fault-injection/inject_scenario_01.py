#!/usr/bin/env python3
"""
Lab 06 — Ticket 1 Fault Injection
Configures FastEthernet0/0 as passive under R4's IPv4 address-family.
A passive EIGRP interface suppresses Hello packets, causing the R1-R4 adjacency
to time out and dropping all of R4's prefixes from the EIGRP domain.

Fault: R4 af-interface Fa0/0 -> passive-interface
  - R4 stops sending and receiving EIGRP Hellos on Fa0/0
  - R1 loses R4 as an EIGRP neighbor after the Hold timer expires (~15 seconds)
  - 192.168.4.0/24, 10.0.0.4/32, and 10.14.0.0/30 disappear from all routing tables

Usage: python3 inject_scenario_01.py
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
    "af-interface FastEthernet0/0",
    "passive-interface",
    "exit-af-interface",
    "exit-address-family",
]

if __name__ == "__main__":
    print("[*] Injecting Ticket 1 fault: passive-interface on R4 Fa0/0...")
    try:
        with ConnectHandler(**R4) as conn:
            conn.enable()
            conn.send_config_set(FAULT_COMMANDS)
            print("[+] Fault injected on R4.")
    except Exception as e:
        print(f"[!] Error: {e}")
    print("[*] Wait ~20 s for the Hold timer to expire, then check:")
    print("    R1# show ip eigrp neighbors")
    print("    Expected: R4 (10.14.0.2) absent from neighbor table")
    print("    R1# show ip route 192.168.4.0")
    print("    Expected: Network not in table")
