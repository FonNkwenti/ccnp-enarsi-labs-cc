#!/usr/bin/env python3
"""Ticket 4: R3 distribute-list removed entirely — no filtering, all R4 routes reach R3."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5003,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 04: R3 — removing distribute-list entirely")

    conn.send_config_set(
        [
            "router eigrp ENARSI",
            "address-family ipv4 unicast autonomous-system 100",
            "no distribute-list prefix BLOCK-R4-LO in FastEthernet0/0",
        ],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R3 distribute-list removed — 192.168.4.0/24 now visible on R3")
    conn.disconnect()


if __name__ == "__main__":
    main()
