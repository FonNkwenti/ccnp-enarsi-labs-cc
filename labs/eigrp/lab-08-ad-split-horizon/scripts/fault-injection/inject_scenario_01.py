#!/usr/bin/env python3
"""Ticket 1: R1 Fa0/0 split-horizon re-enabled — hub-and-spoke routing breaks."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5001,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 01: R1 Fa0/0 — re-enabling ip split-horizon eigrp 100")

    conn.send_config_set(
        ["interface Fa0/0", "ip split-horizon eigrp 100"],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R1 Fa0/0 split-horizon enabled — spokes cannot see each other via R1")
    conn.disconnect()


if __name__ == "__main__":
    main()
