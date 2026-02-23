#!/usr/bin/env python3
"""Ticket 5: R3 distribute-list direction changed to 'out' — filter in wrong direction."""
from netmiko import ConnectHandler


def main():
    conn = ConnectHandler(
        device_type="cisco_ios_telnet",
        host="127.0.0.1",
        port=5003,
        timeout=15,
        global_delay_factor=2,
    )

    print("[*] Injecting Fault 05: R3 — changing distribute-list direction to 'out'")

    conn.send_config_set(
        [
            "router eigrp ENARSI",
            "address-family ipv4 unicast autonomous-system 100",
            "no distribute-list prefix BLOCK-R4-LO in FastEthernet0/0",
            "distribute-list prefix BLOCK-R4-LO out FastEthernet0/0",
        ],
        exit_config_mode=True,
    )

    print("[+] Fault injected: R3 distribute-list applied outbound — R4 routes not filtered on R3")
    conn.disconnect()


if __name__ == "__main__":
    main()
