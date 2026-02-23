#!/usr/bin/env python3
"""Ticket 2: R3 auto-summary enabled — discontiguous network causes routing issues."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5003,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 02: R3 — enabling auto-summary in EIGRP")

    conn.send_config_set(
        [
            "router eigrp ENARSI",
            "address-family ipv4 unicast autonomous-system 100",
            "auto-summary",
        ],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R3 auto-summary enabled — discontiguous network summarization")
    conn.disconnect()


if __name__ == "__main__":
    main()
