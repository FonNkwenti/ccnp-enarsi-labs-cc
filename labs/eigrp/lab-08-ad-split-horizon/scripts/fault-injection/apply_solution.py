#!/usr/bin/env python3
from netmiko import ConnectHandler
import sys
ROUTERS = [
    {"host": "localhost", "port": 5001, "device_type": "cisco_ios_telnet", "username": "", "password": "", "secret": "", "name": "R1"},
    {"host": "localhost", "port": 5002, "device_type": "cisco_ios_telnet", "username": "", "password": "", "secret": "", "name": "R2"},
    {"host": "localhost", "port": 5003, "device_type": "cisco_ios_telnet", "username": "", "password": "", "secret": "", "name": "R3"},
]
CONFIG_DIR = "../../solutions"
print("[*] Restoring Lab 8 to solution state")
sys.exit(0)
