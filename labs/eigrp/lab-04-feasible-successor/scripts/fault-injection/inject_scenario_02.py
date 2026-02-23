#!/usr/bin/env python3
"""Ticket 2: Variance removed — unequal-cost load balancing stops working."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5001,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 02: R1 — removing variance 3 from EIGRP ENARSI")

    conn.send_config_set(
        [
            "router eigrp ENARSI",
            "address-family ipv4 unicast autonomous-system 100",
            "no variance 3",
        ],
        exit_config_mode=True,
    )

    print("[+] Fault injected: variance removed from R1 EIGRP — UCMP disabled")
    conn.disconnect()


if __name__ == "__main__":
    main()
