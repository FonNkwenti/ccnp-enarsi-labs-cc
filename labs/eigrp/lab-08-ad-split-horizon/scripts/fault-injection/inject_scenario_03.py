#!/usr/bin/env python3
"""Ticket 3: R1 static route AD changed to 70 — lower than EIGRP 80, static wins for 10.0.0.3."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5001,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 03: R1 — changing static route AD from 95 to 70 (beats EIGRP AD 80)")

    conn.send_config_set(
        [
            "no ip route 10.0.0.3 255.255.255.255 10.12.0.2 95",
            "ip route 10.0.0.3 255.255.255.255 10.12.0.2 70",
        ],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R1 static route AD=70 — static preferred over EIGRP (AD 80)")
    conn.disconnect()


if __name__ == "__main__":
    main()
