#!/usr/bin/env python3
"""Ticket 3: R3 Fa0/0 summary command removed — 172.16.30.0/23 summary disappears from EIGRP."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5003,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 03: R3 — removing ip summary-address eigrp 100 from Fa0/0")

    conn.send_config_set(
        [
            "interface Fa0/0",
            "no ip summary-address eigrp 100 172.16.30.0 255.255.254.0",
        ],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R3 Fa0/0 summary removed — /24 specifics now advertised instead")
    conn.disconnect()


if __name__ == "__main__":
    main()
