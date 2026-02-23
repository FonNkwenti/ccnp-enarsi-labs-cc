#!/usr/bin/env python3
"""Ticket 3: Topology not updating — neighbors need to be cleared to force re-convergence."""
from netmiko import ConnectHandler

print("[*] Injecting Fault Scenario 03: R3 delay increased but topology not cleared")

net_connect = ConnectHandler(host="localhost", port=5003, device_type="cisco_ios_telnet", username="", password="", secret="")

# Increase delay on R3 Fa0/0 beyond normal
commands = [
    "interface Fa0/0",
    "delay 50000",
]

net_connect.send_config_set(commands)
net_connect.disconnect()

print("[+] Fault injected: extreme delay (50000) on R3 Fa0/0 — topology will not update until neighbors cleared")
