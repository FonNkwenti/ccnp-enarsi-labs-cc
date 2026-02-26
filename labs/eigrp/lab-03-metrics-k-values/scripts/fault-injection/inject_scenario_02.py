#!/usr/bin/env python3
"""
Lab 03 — Ticket 2 fault injector.
Injects an abnormally high delay on R1 Fa1/0 (the direct R1-R3 link).
This causes EIGRP to prefer the two-hop via-R2 path to R3's loopback
over the direct Fa1/0 path.
"""

from netmiko import ConnectHandler

device = {
    "device_type": "cisco_ios_telnet",
    "host": "127.0.0.1",
    "port": 5001,   # R1
    "username": "",
    "password": "",
    "secret": "",
    "global_delay_factor": 2,
}

fault_commands = [
    "interface FastEthernet1/0",
    " delay 5000",
]


def inject():
    print("[*] Injecting Ticket 2 fault: high delay on R1 Fa1/0 (delay 5000)...")
    with ConnectHandler(**device) as conn:
        conn.enable()
        output = conn.send_config_set(fault_commands)
        print(output)
    print("[+] Fault injected. R1's path to R3's loopback will shift to via-R2.")
    print("    Symptom: 'show ip route 10.0.0.3' on R1 shows next-hop via R2, not Fa1/0.")


if __name__ == "__main__":
    inject()
