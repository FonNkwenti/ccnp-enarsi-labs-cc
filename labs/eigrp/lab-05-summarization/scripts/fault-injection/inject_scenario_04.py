#!/usr/bin/env python3
"""Ticket 4: R2 no auto-summary removed — auto-summary re-enabled, discontiguous summarization."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5002,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 04: R2 — removing no auto-summary (re-enables auto-summary)")

    conn.send_config_set(
        [
            "router eigrp 100",
            "no no auto-summary",
        ],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R2 auto-summary re-enabled — discontiguous summarization active")
    conn.disconnect()


if __name__ == "__main__":
    main()
