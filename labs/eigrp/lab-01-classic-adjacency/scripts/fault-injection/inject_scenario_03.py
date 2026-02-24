#!/usr/bin/env python3
"""
Lab 01 — Ticket 09-3: R3 Loopback Unreachable
Fault: R3 is missing the network statement for its Loopback0 (10.0.0.3/32).
Symptom: All adjacencies form normally; R1 and R2 cannot ping 10.0.0.3; prefix absent from remote routing tables.
"""

from netmiko import ConnectHandler

R3 = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5003,
    "username": "",
    "password": "",
    "global_delay_factor": 2,
}

FAULT_COMMANDS = [
    "router eigrp 100",
    " no network 10.0.0.3 0.0.0.0",
]


def inject():
    print("[*] Injecting Scenario 03: Missing network stmt for R3 Loopback0...")
    try:
        with ConnectHandler(**R3) as conn:
            conn.enable()
            conn.send_config_set(FAULT_COMMANDS)
            print("[+] Fault injected on R3.")
            print("[*] Diagnose with: show ip route on R1 -- 10.0.0.3 should be absent")
    except Exception as e:
        print(f"[!] Error: {e}")


if __name__ == "__main__":
    inject()
