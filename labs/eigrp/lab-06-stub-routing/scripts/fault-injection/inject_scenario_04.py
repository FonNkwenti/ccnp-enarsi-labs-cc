#!/usr/bin/env python3
"""Ticket 4: R4 EIGRP network 10.0.0.4 removed — Lo0 not advertised, R1 loses 10.0.0.4/32."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5004,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 04: R4 — removing network 10.0.0.4 0.0.0.0 from EIGRP")

    conn.send_config_set(
        [
            "router eigrp 100",
            "no network 10.0.0.4 0.0.0.0",
        ],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R4 Lo0 network removed — 10.0.0.4/32 not advertised via EIGRP")
    conn.disconnect()


if __name__ == "__main__":
    main()
