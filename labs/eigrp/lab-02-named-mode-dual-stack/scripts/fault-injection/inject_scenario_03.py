#!/usr/bin/env python3
"""Ticket 3: K-value mismatch on IPv6 EIGRP 100 process — IPv6 neighbors drop."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5001,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Applying custom K-values to IPv6 EIGRP 100 on R1 (mismatch with default)...")

    commands = [
        "ipv6 router eigrp 100",
        "metric weights 0 2 0 1 0 0",
    ]

    conn.send_config_set(commands, exit_config_mode=True)
    print("[+] Fault injected: IPv6 K1=2 on R1 EIGRP 100 (vs default K1=1)")

    conn.disconnect()


if __name__ == "__main__":
    main()
