#!/usr/bin/env python3
"""Ticket 3: R2 Fa0/0 bandwidth 10 — metric to R1 recalculates, topology changes unexpectedly."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5002,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 03: R2 Fa0/0 bandwidth 10 — incorrect metric recalculation")

    conn.send_config_set(
        ["interface Fa0/0", "bandwidth 10"],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R2 Fa0/0 bandwidth reduced to 10 Kbps")
    conn.disconnect()


if __name__ == "__main__":
    main()
