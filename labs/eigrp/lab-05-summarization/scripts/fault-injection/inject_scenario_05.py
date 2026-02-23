#!/usr/bin/env python3
"""Ticket 5: R3 Lo1 and Lo2 removed — all R3 summarized routes drop from EIGRP."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5003,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 05: R3 — removing Lo1 and Lo2 (summary 172.16.30.0/23 drops)")

    conn.send_config_set(
        ["no interface Loopback1", "no interface Loopback2"],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R3 Lo1/Lo2 removed — 172.16.30.0/23 summary withdrawn from EIGRP")
    conn.disconnect()


if __name__ == "__main__":
    main()
