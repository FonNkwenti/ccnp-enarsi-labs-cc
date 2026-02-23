#!/usr/bin/env python3
"""Ticket 3: R3 prefix-list seq 5 changed from deny to permit — 192.168.4.0/24 passes filter."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5003,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 03: R3 — changing prefix-list seq 5 from deny to permit 192.168.4.0/24")

    conn.send_config_set(
        [
            "no ip prefix-list BLOCK-R4-LO seq 5 deny 192.168.4.0/24",
            "ip prefix-list BLOCK-R4-LO seq 5 permit 192.168.4.0/24",
        ],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R3 filter inverted — 192.168.4.0/24 now permitted (should be denied)")
    conn.disconnect()


if __name__ == "__main__":
    main()
