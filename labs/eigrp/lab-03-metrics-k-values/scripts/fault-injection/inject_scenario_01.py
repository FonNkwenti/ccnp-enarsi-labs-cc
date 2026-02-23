#!/usr/bin/env python3
"""Ticket 1: Metrics not reflecting bandwidth change — interface bandwidth not applied."""
from netmiko import ConnectHandler

print("[*] Injecting Fault Scenario 01: R2 Fa0/0 missing bandwidth command")

net_connect = ConnectHandler(host="localhost", port=5002, device_type="cisco_ios_telnet", username="", password="", secret="")

# Remove the bandwidth command from R2 Fa0/0
commands = [
    "interface Fa0/0",
    "no bandwidth",
]

net_connect.send_config_set(commands)
net_connect.disconnect()

print("[+] Fault injected: bandwidth command removed from R2 Fa0/0")
