#!/usr/bin/env python3
"""Ticket 1: R4 AS mismatch — already in initial-configs, inject again for per-ticket practice."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5004,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 01: R4 — AS mismatch (router eigrp 200 instead of ENARSI/100)")

    conn.send_config_set(
        [
            "no router eigrp ENARSI",
            "router eigrp 200",
            "address-family ipv4 unicast autonomous-system 200",
            "network 10.0.0.4 0.0.0.0",
            "network 10.14.0.0 0.0.0.3",
            "network 192.168.4.0",
            "eigrp stub receive-only",
        ],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R4 running EIGRP AS 200 — no adjacency with R1 (ENARSI/100)")
    conn.disconnect()


if __name__ == "__main__":
    main()
