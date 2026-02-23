#!/usr/bin/env python3
"""Ticket 5: R2 EIGRP network statements for Lo1/Lo2 removed — summary 172.16.20.0/23 drops."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5002,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 05: R2 — removing network stmts for 172.16.20.0 and 172.16.21.0")

    conn.send_config_set(
        [
            "router eigrp ENARSI",
            "address-family ipv4 unicast autonomous-system 100",
            "no network 172.16.20.0 0.0.0.255",
            "no network 172.16.21.0 0.0.0.255",
        ],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R2 Lo1/Lo2 networks removed — 172.16.20.0/23 summary withdrawn")
    conn.disconnect()


if __name__ == "__main__":
    main()
