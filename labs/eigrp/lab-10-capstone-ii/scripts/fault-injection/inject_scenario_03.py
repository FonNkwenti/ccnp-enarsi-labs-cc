#!/usr/bin/env python3
"""Ticket 3: R3 K-value mismatch — metric weights 0 1 1 1 0 0 causes adjacency drops."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5003,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 03: R3 — setting metric weights 0 1 1 1 0 0 (K2=1 mismatch)")

    conn.send_config_set(
        [
            "router eigrp ENARSI",
            "address-family ipv4 unicast autonomous-system 100",
            "metric weights 0 1 1 1 0 0",
        ],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R3 K-value mismatch (K2=1) — adjacency with R1 and R2 drops")
    conn.disconnect()


if __name__ == "__main__":
    main()
