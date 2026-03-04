#!/usr/bin/env python3
"""
Lab 07 — Ticket 2 Fault Injection
Inserts a spurious 'route-map RM_DENY_TAG_200 permit 5' on R4 with no match conditions.
Because sequence 5 is lower than the existing deny 10, it matches all routes first,
bypassing the tag-200 deny clause entirely.

Effect:
  - R4's tag-200 filter becomes ineffective
  - 172.16.20.0/23 (tagged 200 by R2) now enters R4's routing table
  - Route-map hit counters on seq 5 increment; seq 10 never fires

Usage: python3 inject_scenario_02.py
"""

from netmiko import ConnectHandler

R4 = {
    "device_type": "cisco_ios_telnet", "host": "127.0.0.1", "port": 5004,
    "username": "", "password": "", "secret": "", "global_delay_factor": 2,
}

FAULT_COMMANDS = [
    "route-map RM_DENY_TAG_200 permit 5",
]

if __name__ == "__main__":
    print("[*] Injecting Ticket 2 fault: spurious permit 5 added to RM_DENY_TAG_200 on R4...")
    try:
        with ConnectHandler(**R4) as conn:
            conn.enable()
            conn.send_config_set(FAULT_COMMANDS)
            print("[+] Fault injected on R4.")
    except Exception as e:
        print(f"[!] Error: {e}")
    print("[*] Wait ~15 s for EIGRP update, then check:")
    print("    R4# show ip route 172.16.20.0")
    print("    Expected: 172.16.20.0/23 now present (tag filter bypassed)")
    print("    R4# show route-map RM_DENY_TAG_200")
    print("    Expected: permit 5 with no match clauses shown at top")
