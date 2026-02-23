#!/usr/bin/env python3
"""Ticket 4: Classic mode router eigrp 100 re-enabled (incomplete migration)"""
from netmiko import ConnectHandler

def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5001,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Re-enabling classic EIGRP mode on R1...")

    commands = [
        "router eigrp 100",
        "network 10.0.0.0 0.0.0.255",
        "network 10.12.0.0 0.0.0.3",
        "network 10.13.0.0 0.0.0.3",
        "network 10.23.0.0 0.0.0.3",
        "no auto-summary",
    ]

    conn.send_config_set(commands, exit_config_mode=True)
    print("[+] Fault injected: Classic mode (router eigrp 100) re-enabled on R1")

    conn.disconnect()

if __name__ == "__main__":
    main()
