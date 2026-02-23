#!/usr/bin/env python3
"""Ticket 1: R2 Lo2 removed — summary 172.16.20.0/23 covers 172.16.21.x with null0 black hole."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5002,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 01: R2 — removing Lo2 (172.16.21.1), creating summary black hole")

    conn.send_config_set(
        ["no interface Loopback2"],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R2 Lo2 removed — 172.16.21.0/24 now null0 via summary")
    conn.disconnect()


if __name__ == "__main__":
    main()
