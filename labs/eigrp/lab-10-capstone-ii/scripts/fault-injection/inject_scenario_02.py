#!/usr/bin/env python3
"""Ticket 2: R2 loopback networks removed from EIGRP — summarized route 172.16.20.0/23 disappears."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5002,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 02: R2 — removing loopback networks from EIGRP 100")

    conn.send_config_set(
        [
            "router eigrp 100",
            "no network 172.16.20.0 0.0.0.255",
            "no network 172.16.21.0 0.0.0.255",
        ],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R2 loopbacks not in EIGRP — 172.16.20.0/23 summary withdrawn from all neighbors")
    conn.disconnect()


if __name__ == "__main__":
    main()
