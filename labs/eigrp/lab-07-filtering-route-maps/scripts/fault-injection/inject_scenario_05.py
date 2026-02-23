#!/usr/bin/env python3
"""Ticket 5: R4 no auto-summary removed — auto-summary active, 192.168.4.0/24 summarized to /16."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5004,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 05: R4 — removing 'no auto-summary' (re-enables auto-summary)")

    conn.send_config_set(
        [
            "router eigrp 100",
            "no no auto-summary",
        ],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R4 auto-summary re-enabled — 192.168.4.0/24 summarized to 192.168.0.0/16, bypasses /24 filter")
    conn.disconnect()


if __name__ == "__main__":
    main()
