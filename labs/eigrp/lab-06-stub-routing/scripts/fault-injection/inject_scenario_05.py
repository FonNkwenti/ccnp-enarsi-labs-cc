#!/usr/bin/env python3
"""Ticket 5: R1 EIGRP network 10.14.0.0 removed — R1 Fa1/1 not in EIGRP, R4 loses adjacency."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5001,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 05: R1 — removing network 10.14.0.0 0.0.0.3 from EIGRP")

    conn.send_config_set(
        [
            "router eigrp ENARSI",
            "address-family ipv4 unicast autonomous-system 100",
            "no network 10.14.0.0 0.0.0.3",
        ],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R1 Fa1/1 not in EIGRP — R4 adjacency lost from R1's side")
    conn.disconnect()


if __name__ == "__main__":
    main()
