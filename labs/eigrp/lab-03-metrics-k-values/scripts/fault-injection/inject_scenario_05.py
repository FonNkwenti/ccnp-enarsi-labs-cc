#!/usr/bin/env python3
"""Ticket 5: Successor unchanged after delay modification — R3 interface not in EIGRP."""
from netmiko import ConnectHandler

print("[*] Injecting Fault Scenario 05: R3 interface excluded from EIGRP routing")

net_connect = ConnectHandler(host="localhost", port=5003, device_type="cisco_ios_telnet", username="", password="", secret="")

# Mark R3 Fa0/0 as passive, preventing EIGRP from using it
commands = [
    "router eigrp ENARSI",
    "address-family ipv4 unicast autonomous-system 100",
    "passive-interface Fa0/0",
]

net_connect.send_config_set(commands)
net_connect.disconnect()

print("[+] Fault injected: R3 Fa0/0 set as passive-interface in EIGRP")
