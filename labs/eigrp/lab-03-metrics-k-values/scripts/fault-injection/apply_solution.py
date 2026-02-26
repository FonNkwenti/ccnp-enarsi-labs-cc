#!/usr/bin/env python3
"""
Lab 03 — Restore solution state on all routers.
Removes all injected faults and applies the Lab 03 solution configuration:
  - R1: K-values restored to default; bandwidth 512 + delay 2000 on Fa0/0 (solution state)
  - R1: Fa1/0 delay restored to default (removes Ticket 2 fault)
  - R2: K-values restored to default (removes Ticket 3 fault)
  - R3: no changes required (no faults target R3)
"""

from netmiko import ConnectHandler

ROUTERS = [
    {
        "device_type": "cisco_ios_telnet",
        "host": "127.0.0.1",
        "port": 5001,
        "username": "",
        "password": "",
        "secret": "",
        "global_delay_factor": 2,
        "name": "R1",
    },
    {
        "device_type": "cisco_ios_telnet",
        "host": "127.0.0.1",
        "port": 5002,
        "username": "",
        "password": "",
        "secret": "",
        "global_delay_factor": 2,
        "name": "R2",
    },
]

RESTORE = {
    "R1": [
        # Restore K-values to default (fixes Ticket 1 fault)
        "router eigrp ENARSI",
        " address-family ipv4 unicast autonomous-system 100",
        "  metric weights 0 1 0 1 0 0",
        "  exit-address-family",
        # Restore Fa1/0 delay to default (fixes Ticket 2 fault)
        "interface FastEthernet1/0",
        " no delay",
        # Ensure solution-state metric tuning on Fa0/0
        "interface FastEthernet0/0",
        " bandwidth 512",
        " delay 2000",
    ],
    "R2": [
        # Restore K-values to default (fixes Ticket 3 fault)
        "router eigrp ENARSI",
        " address-family ipv4 unicast autonomous-system 100",
        "  no metric weights",
        "  exit-address-family",
    ],
}


def restore(router_info):
    device = {k: v for k, v in router_info.items() if k != "name"}
    name = router_info["name"]
    commands = RESTORE[name]
    print(f"[*] Restoring {name}...")
    try:
        with ConnectHandler(**device) as conn:
            conn.enable()
            output = conn.send_config_set(commands)
            print(output)
        print(f"[+] {name} restored to solution state.")
    except Exception as e:
        print(f"[!] Error restoring {name}: {e}")


if __name__ == "__main__":
    print("Lab 03 — Restoring all routers to solution state")
    print("=" * 55)
    for router in ROUTERS:
        restore(router)
    print("=" * 55)
    print("[*] Done. Verify: show ip eigrp neighbors on all routers.")
    print("[*] R1 route to 10.0.0.2/32 should be via Fa1/0 (R3 transit).")
