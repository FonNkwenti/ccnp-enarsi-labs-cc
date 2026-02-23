#!/usr/bin/env python3
"""Ticket 4: Bandwidth command applied but K2=1 prevents it from affecting metric."""
from netmiko import ConnectHandler

print("[*] Injecting Fault Scenario 04: Bandwidth applied with K2=1 (ineffective)")

net_connect = ConnectHandler(host="localhost", port=5002, device_type="cisco_ios_telnet", username="", password="", secret="")

# Set K2=1 on R2, which makes bandwidth changes ineffective
commands = [
    "router eigrp 100",
    "metric weights 0 1 1 1 0 0",
]

net_connect.send_config_set(commands)
net_connect.disconnect()

print("[+] Fault injected: K2=1 set on R2, making bandwidth manipulation ineffective")
