#!/usr/bin/env python3
"""Ticket 4: R1 passive-interface default — all EIGRP adjacencies lost on R1."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5001,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 04: R1 — adding passive-interface default to EIGRP ENARSI")

    conn.send_config_set(
        [
            "router eigrp ENARSI",
            "address-family ipv4 unicast autonomous-system 100",
            "passive-interface default",
            "no passive-interface Loopback0",
        ],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R1 passive-interface default — R1 loses all EIGRP neighbors")
    conn.disconnect()


if __name__ == "__main__":
    main()
