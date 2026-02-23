#!/usr/bin/env python3
"""Ticket 2: R2 IPv6 EIGRP removed — dual-stack IPv6 adjacency drops on R2."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5002,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 02: R2 — removing ipv6 eigrp ENARSI from all interfaces")

    conn.send_config_set(
        [
            "interface Lo0",
            "no ipv6 eigrp ENARSI",
            "interface Fa0/0",
            "no ipv6 eigrp ENARSI",
            "interface Fa0/1",
            "no ipv6 eigrp ENARSI",
        ],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R2 IPv6 EIGRP removed — IPv6 routes from R2 lost across topology")
    conn.disconnect()


if __name__ == "__main__":
    main()
