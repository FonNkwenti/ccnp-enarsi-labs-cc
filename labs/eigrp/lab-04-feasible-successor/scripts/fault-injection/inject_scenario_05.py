#!/usr/bin/env python3
"""Ticket 5: R3 Fa0/1 delay 50000 — Feasibility Condition fails via alternate path."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5003,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 05: R3 Fa0/1 delay 50000 — FC fails via R3→R2 alternate path")

    conn.send_config_set(
        ["interface Fa0/1", "delay 50000"],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R3 Fa0/1 delay set to 50000 — RD via R3 now exceeds FD, FC not met")
    conn.disconnect()


if __name__ == "__main__":
    main()
