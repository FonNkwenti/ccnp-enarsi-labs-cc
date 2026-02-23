#!/usr/bin/env python3
"""Ticket 1: R4 stub changed to 'eigrp stub' only — leaks transit routes, no summary/connected."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5004,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 01: R4 — changing stub to bare 'eigrp stub' (leaks transit routes)")

    conn.send_config_set(
        [
            "router eigrp 100",
            "no eigrp stub connected summary",
            "eigrp stub",
        ],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R4 stub set to bare 'eigrp stub' — may advertise transit routes")
    conn.disconnect()


if __name__ == "__main__":
    main()
