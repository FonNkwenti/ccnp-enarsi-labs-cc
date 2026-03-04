#!/usr/bin/env python3
"""
Lab 07 — Ticket 3 Fault Injection
Removes the 'permit 0.0.0.0/0 le 32' catch-all entry (seq 10) from R3's
PFX_DENY_R4_STUB prefix-list. The implicit deny at the end of the prefix-list
now blocks ALL inbound routes on R3 Fa0/0, not just 192.168.4.0/24.

Effect:
  - R3 loses all EIGRP-learned routes received from R1 via Fa0/0
  - R3 routing table retains only directly connected and R2-learned routes (via Fa0/1)
  - EIGRP adjacency with R1 stays UP (adjacency is control-plane, not data-plane filtered)

Usage: python3 inject_scenario_03.py
"""

from netmiko import ConnectHandler

R3 = {
    "device_type": "cisco_ios_telnet", "host": "127.0.0.1", "port": 5003,
    "username": "", "password": "", "secret": "", "global_delay_factor": 2,
}

FAULT_COMMANDS = [
    "no ip prefix-list PFX_DENY_R4_STUB seq 10",
]

if __name__ == "__main__":
    print("[*] Injecting Ticket 3 fault: removing permit catch-all from PFX_DENY_R4_STUB on R3...")
    try:
        with ConnectHandler(**R3) as conn:
            conn.enable()
            conn.send_config_set(FAULT_COMMANDS)
            print("[+] Fault injected on R3.")
    except Exception as e:
        print(f"[!] Error: {e}")
    print("[*] Wait ~15 s for EIGRP to reconverge, then check:")
    print("    R3# show ip route eigrp")
    print("    Expected: Routes from R1 absent (10.0.0.1, 10.0.0.4, R4 routes)")
    print("    R3# show ip eigrp neighbors")
    print("    Expected: R1 still adjacent (adjacency unaffected by distribute-list)")
    print("    R3# show ip prefix-list PFX_DENY_R4_STUB")
    print("    Expected: Only seq 5 deny 192.168.4.0/24 — seq 10 missing")
