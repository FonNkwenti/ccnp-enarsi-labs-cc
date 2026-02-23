#!/usr/bin/env python3
"""Ticket 5: R1 no ip split-horizon eigrp 100 applied to Fa1/0 instead of Fa0/0 (wrong interface)."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5001,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 05: R1 — moving no split-horizon from Fa0/0 to Fa1/0 (wrong interface)")

    conn.send_config_set(
        [
            "interface Fa0/0",
            "ip split-horizon eigrp 100",
            "interface Fa1/0",
            "no ip split-horizon eigrp 100",
        ],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R1 split-horizon disabled on Fa1/0 instead of Fa0/0 — hub-spoke still broken")
    conn.disconnect()


if __name__ == "__main__":
    main()
