#!/usr/bin/env python3
"""Ticket 2: IPv6 unicast routing disabled; IPv6 neighbors won't form"""
from netmiko import ConnectHandler

def main():
    for port, rname in [(5001, "R1"), (5002, "R2"), (5003, "R3")]:
        conn = ConnectHandler(
            device_type="cisco_ios_telnet",
            host="127.0.0.1",
            port=port,
            timeout=15,
            global_delay_factor=2,
        )

        print(f"[*] Disabling IPv6 unicast routing on {rname}...")

        commands = ["no ipv6 unicast-routing"]
        conn.send_config_set(commands, exit_config_mode=True)

        conn.disconnect()

    print("[+] Fault injected: IPv6 unicast routing disabled on all routers")

if __name__ == "__main__":
    main()
