#!/usr/bin/env python3
"""
Lab 04 — Ticket 1 Fault Injection
Breaks the Feasibility Condition for R1's route to 10.0.0.2/32 by increasing
R2's Loopback0 delay. This raises the RD R2 advertises for its own loopback,
pushing it above R1's current FD via R3 and causing FC to fail.

Fault: R2 Lo0 delay set to 5300 (default: 5000)
  - R2 RD for 10.0.0.2 = (10^7/8000 + 5300) * 256 = 1,676,800
  - R1 FD via R3 = 1,651,200
  - 1,676,800 >= 1,651,200  ->  FC FAILS  ->  no Feasible Successor on R1

Usage: python3 inject_scenario_01.py
"""

from netmiko import ConnectHandler

R2 = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5002,
    "username": "",
    "password": "",
    "secret": "",
    "global_delay_factor": 2,
}

FAULT_COMMANDS = [
    "interface Loopback0",
    "delay 5300",
]

if __name__ == "__main__":
    print("[*] Injecting Ticket 1 fault: elevating R2 Lo0 delay to break FC on R1...")
    try:
        with ConnectHandler(**R2) as conn:
            conn.enable()
            conn.send_config_set(FAULT_COMMANDS)
            print("[+] Fault injected on R2.")
    except Exception as e:
        print(f"[!] Error: {e}")
    print("[*] Wait ~30 s for EIGRP to reconverge, then check:")
    print("    R1# show ip eigrp topology 10.0.0.2 255.255.255.255")
    print("    Expected: 'Feasibility condition not met' on the via-R2 path")
