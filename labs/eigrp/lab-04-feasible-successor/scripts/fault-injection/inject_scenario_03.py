#!/usr/bin/env python3
"""
Lab 04 — Ticket 3 Fault Injection
Elevates delay on R3 fa0/1 (R3 toward R2). This changes R3's reported metric
for R2's networks, altering which path R1 uses as successor and breaking the
Feasibility Condition for the alternate path.

Fault: R3 fa0/1 delay set to 30000 (default: 100)
  - R3 RD for 10.0.0.2 rises sharply
  - R1's best path to 10.0.0.2 shifts to direct via R2 fa0/0
  - R3's new RD > R1's FD via direct  ->  via-R3 path fails FC  ->  no FS
  - On R1 fa0/0 failure, DUAL enters ACTIVE for 10.0.0.2 (no instant failover)

Usage: python3 inject_scenario_03.py
"""

from netmiko import ConnectHandler

R3 = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5003,
    "username": "",
    "password": "",
    "secret": "",
    "global_delay_factor": 2,
}

FAULT_COMMANDS = [
    "interface FastEthernet0/1",
    "delay 30000",
]

if __name__ == "__main__":
    print("[*] Injecting Ticket 3 fault: elevating R3 fa0/1 delay to 30000...")
    try:
        with ConnectHandler(**R3) as conn:
            conn.enable()
            conn.send_config_set(FAULT_COMMANDS)
            print("[+] Fault injected on R3.")
    except Exception as e:
        print(f"[!] Error: {e}")
    print("[*] Wait ~30 s for EIGRP to reconverge, then check:")
    print("    R1# show ip eigrp topology 10.0.0.2 255.255.255.255")
    print("    Expected: direct via-R2 is now Successor; no Feasible Successor listed")
    print("    R3# show interface FastEthernet0/1 | include DLY")
    print("    Expected: DLY 300000 usec (= delay 30000 x 10 usec)")
