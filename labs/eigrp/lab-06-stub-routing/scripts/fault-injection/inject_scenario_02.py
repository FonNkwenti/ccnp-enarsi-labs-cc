#!/usr/bin/env python3
"""Ticket 2: R4 stub set to receive-only — R4 advertises nothing, R1 loses 10.0.0.4 and 192.168.4.0."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5004,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 02: R4 — changing stub to 'receive-only' (advertises nothing)")

    conn.send_config_set(
        [
            "router eigrp ENARSI",
            "address-family ipv4 unicast autonomous-system 100",
            "no eigrp stub connected summary",
            "eigrp stub receive-only",
        ],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R4 stub receive-only — no routes advertised to R1")
    conn.disconnect()


if __name__ == "__main__":
    main()
