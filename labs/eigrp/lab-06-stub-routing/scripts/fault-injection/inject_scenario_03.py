#!/usr/bin/env python3
"""Ticket 3: R4 EIGRP network 10.14.0.0 removed — adjacency to R1 drops."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5004,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 03: R4 — removing network 10.14.0.0 0.0.0.3 from EIGRP")

    conn.send_config_set(
        [
            "router eigrp ENARSI",
            "address-family ipv4 unicast autonomous-system 100",
            "no network 10.14.0.0 0.0.0.3",
        ],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R4 EIGRP network 10.14.0.0/30 removed — R4 loses adjacency with R1")
    conn.disconnect()


if __name__ == "__main__":
    main()
