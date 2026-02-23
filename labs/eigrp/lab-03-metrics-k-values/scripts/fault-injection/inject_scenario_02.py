#!/usr/bin/env python3
"""Ticket 2: K-value mismatch causing adjacency drop."""
from netmiko import ConnectHandler

print("[*] Injecting Fault Scenario 02: K-value mismatch on R2")

net_connect = ConnectHandler(host="localhost", port=5002, device_type="cisco_ios_telnet", username="", password="", secret="")

# Set K2=1 on R2 (mismatch with default K2=0)
commands = [
    "router eigrp ENARSI",
    "address-family ipv4 unicast autonomous-system 100",
    "metric weights 0 1 1 1 0 0",
]

net_connect.send_config_set(commands)
net_connect.disconnect()

print("[+] Fault injected: K-value mismatch (K2=1) on R2 EIGRP")
