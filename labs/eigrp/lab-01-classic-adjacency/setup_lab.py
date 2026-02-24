#!/usr/bin/env python3
"""
Lab 01 -- EIGRP Classic Mode: Neighbor Adjacency & Basic IPv4
Setup script: Pushes initial-configs to all routers via GNS3 console (Telnet).

Usage: python3 setup_lab.py

Prerequisites:
  - GNS3 running with R1, R2, R3 all started
  - pip install netmiko
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
    {
        "device_type": "cisco_ios_telnet",
        "host": "127.0.0.1",
        "port": 5003,
        "username": "",
        "password": "",
        "secret": "",
        "global_delay_factor": 2,
        "name": "R3",
    },
]

# Initial configs: IP addressing only, no EIGRP (student configures EIGRP)
CONFIGS = {
    "R1": [
        "hostname R1",
        "no ip domain-lookup",
        "interface Loopback0",
        " description Lo0 - Router ID",
        " ip address 10.0.0.1 255.255.255.255",
        "interface FastEthernet0/0",
        " description Link to R2 fa0/0 -- 10.12.0.0/30",
        " ip address 10.12.0.1 255.255.255.252",
        " no shutdown",
        "interface FastEthernet1/0",
        " description Link to R3 fa0/0 -- 10.13.0.0/30",
        " ip address 10.13.0.1 255.255.255.252",
        " no shutdown",
    ],
    "R2": [
        "hostname R2",
        "no ip domain-lookup",
        "interface Loopback0",
        " description Lo0 - Router ID",
        " ip address 10.0.0.2 255.255.255.255",
        "interface FastEthernet0/0",
        " description Link to R1 fa0/0 -- 10.12.0.0/30",
        " ip address 10.12.0.2 255.255.255.252",
        " no shutdown",
        "interface FastEthernet0/1",
        " description Link to R3 fa0/1 -- 10.23.0.0/30",
        " ip address 10.23.0.1 255.255.255.252",
        " no shutdown",
    ],
    "R3": [
        "hostname R3",
        "no ip domain-lookup",
        "interface Loopback0",
        " description Lo0 - Router ID",
        " ip address 10.0.0.3 255.255.255.255",
        "interface FastEthernet0/0",
        " description Link to R1 fa1/0 -- 10.13.0.0/30",
        " ip address 10.13.0.2 255.255.255.252",
        " no shutdown",
        "interface FastEthernet0/1",
        " description Link to R2 fa0/1 -- 10.23.0.0/30",
        " ip address 10.23.0.2 255.255.255.252",
        " no shutdown",
    ],
}


def push_config(router_info):
    device = {k: v for k, v in router_info.items() if k != "name"}
    name = router_info["name"]
    commands = CONFIGS[name]
    print(f"[*] Connecting to {name} on port {device['port']}...")
    try:
        with ConnectHandler(**device) as conn:
            conn.enable()
            conn.send_config_set(commands)
            print(f"[+] {name} configured successfully.")
    except Exception as e:
        print(f"[!] Error configuring {name}: {e}")


if __name__ == "__main__":
    print("Lab 01 Setup -- Pushing initial-configs (IP addressing only, no EIGRP)")
    print("=" * 60)
    for router in ROUTERS:
        push_config(router)
    print("=" * 60)
    print("[*] Done. Verify with: show ip interface brief")
    print("[*] Now configure EIGRP classic mode (AS 100) per the workbook.")
