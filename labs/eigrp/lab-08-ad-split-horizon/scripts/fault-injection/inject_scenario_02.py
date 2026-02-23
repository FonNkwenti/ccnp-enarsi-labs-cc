#!/usr/bin/env python3
"""Ticket 2: R1 EIGRP AD set to 200 for both internal and external — too high, static preferred."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5001,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 02: R1 — setting EIGRP distance eigrp 200 200 (too high)")

    conn.send_config_set(
        [
            "router eigrp ENARSI",
            "address-family ipv4 unicast autonomous-system 100",
            "distance eigrp 200 200",
        ],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R1 EIGRP AD=200 — static route (AD 95) preferred over EIGRP")
    conn.disconnect()


if __name__ == "__main__":
    main()
