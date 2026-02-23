#!/usr/bin/env python3
"""Ticket 1: IPv6 Loopback not advertised in EIGRP"""
from netmiko import ConnectHandler

def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5001,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Removing IPv6 EIGRP from Lo0 on R1...")

    commands = [
        "interface Lo0",
        "no ipv6 eigrp ENARSI",
    ]

    conn.send_config_set(commands, exit_config_mode=True)
    print("[+] Fault injected: R1 Lo0 no longer participates in IPv6 EIGRP")

    conn.disconnect()

if __name__ == "__main__":
    main()
