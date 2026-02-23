#!/usr/bin/env python3
"""Ticket 4: IPv6 EIGRP process removed from R1 — R1 loses all IPv6 neighbors."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5001,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 04: R1 — removing ipv6 router eigrp 100 process")

    conn.send_config_set(
        [
            "no ipv6 router eigrp 100",
        ],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R1 IPv6 EIGRP process removed — all IPv6 EIGRP neighbors lost on R1")
    conn.disconnect()


if __name__ == "__main__":
    main()
