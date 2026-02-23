#!/usr/bin/env python3
"""Ticket 2: R3 prefix-list permit-all entry removed — implicit deny blocks all EIGRP updates."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5003,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 02: R3 — removing 'permit 0.0.0.0/0 le 32' from BLOCK-R4-LO")

    conn.send_config_set(
        ["no ip prefix-list BLOCK-R4-LO seq 10 permit 0.0.0.0/0 le 32"],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R3 prefix-list implicit deny now blocks ALL EIGRP updates inbound")
    conn.disconnect()


if __name__ == "__main__":
    main()
