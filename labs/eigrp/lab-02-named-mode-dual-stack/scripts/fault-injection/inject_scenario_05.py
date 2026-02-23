#!/usr/bin/env python3
"""Ticket 5: Passive interface on IPv6 EIGRP 100 — IPv6 neighbors won't form via Fa0/0."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5002,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Setting Fa0/0 as passive in IPv6 EIGRP 100 on R2...")

    commands = [
        "ipv6 router eigrp 100",
        "passive-interface Fa0/0",
    ]

    conn.send_config_set(commands, exit_config_mode=True)
    print("[+] Fault injected: Fa0/0 passive in IPv6 EIGRP 100 on R2 (IPv4 still active)")

    conn.disconnect()


if __name__ == "__main__":
    main()
