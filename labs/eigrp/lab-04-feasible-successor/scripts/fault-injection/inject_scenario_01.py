#!/usr/bin/env python3
"""Ticket 1: No Feasible Successor — R2 Fa0/1 bandwidth set to 10 Kbps, RD via R2 exceeds FD."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5002,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 01: R2 Fa0/1 bandwidth 10 — RD via R2 exceeds FD, no FS for R3")

    conn.send_config_set(
        ["interface Fa0/1", "bandwidth 10"],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R2 Fa0/1 bandwidth reduced to 10 Kbps")
    conn.disconnect()


if __name__ == "__main__":
    main()
