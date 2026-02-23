#!/usr/bin/env python3
"""Ticket 4: R1 Fa1/0 shutdown — primary link down, no FS available, slow convergence."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5001,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 04: R1 Fa1/0 shutdown — primary link to R3 down, no FS")

    conn.send_config_set(
        ["interface Fa1/0", "shutdown"],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R1 Fa1/0 shutdown — DUAL recalculation triggered, no immediate failover")
    conn.disconnect()


if __name__ == "__main__":
    main()
