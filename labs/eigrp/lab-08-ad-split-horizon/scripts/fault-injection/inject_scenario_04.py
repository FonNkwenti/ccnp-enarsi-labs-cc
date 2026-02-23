#!/usr/bin/env python3
"""Ticket 4: R1 EIGRP distance eigrp 90 80 — external AD lower than internal (misconfigured)."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5001,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 04: R1 — setting distance eigrp 90 80 (external lower than internal)")

    conn.send_config_set(
        [
            "router eigrp ENARSI",
            "address-family ipv4 unicast autonomous-system 100",
            "distance eigrp 90 80",
        ],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R1 distance eigrp 90 80 — external routes preferred over internal (wrong)")
    conn.disconnect()


if __name__ == "__main__":
    main()
