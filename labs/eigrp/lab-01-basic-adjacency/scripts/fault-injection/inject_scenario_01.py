#!/usr/bin/env python3
"""
Fault Injection Script Template: AS Number Mismatch

Injects: EIGRP AS Number Mismatch
Target Device: R2
Fault Type: Protocol Parameter Mismatch

This script connects to R2 via console and changes the EIGRP AS number
from 100 to 200, preventing adjacency formation with R1.
"""

import socket
import time
import sys

# Device Configuration
DEVICE_NAME = "R2"
CONSOLE_HOST = "127.0.0.1"
CONSOLE_PORT = 5002
TIMEOUT = 10

# Fault Configuration Commands
FAULT_COMMANDS = [
    "configure terminal",
    "no router eigrp 100",
    "router eigrp 200",
    "eigrp router-id 2.2.2.2",
    "network 2.2.2.2 0.0.0.0",
    "network 10.0.12.0 0.0.0.3",
    "network 10.0.23.0 0.0.0.3",
    "passive-interface Loopback0",
    "no auto-summary",
    "end",
    "write memory",
]

def inject_fault():
    """Connect to device and inject the fault configuration."""
    print(f"[*] Connecting to {DEVICE_NAME} on {CONSOLE_HOST}:{CONSOLE_PORT}...")
    
    try:
        tn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tn.settimeout(5)
        tn.connect((CONSOLE_HOST, CONSOLE_PORT))
        print(f"[+] Connected to {DEVICE_NAME}")
        
        # Press Enter to get prompt
        tn.sendall(b"\r\n")
        time.sleep(1)
        
        # Enter enable mode
        tn.sendall(b"enable\n")
        time.sleep(1)
        
        # Apply fault commands
        print(f"[*] Injecting fault configuration...")
        print(f"[*] Changing EIGRP AS from 100 to 200 (FAULT)")
        for cmd in FAULT_COMMANDS:
            print(f"    {cmd}")
            tn.sendall(f"{cmd}\n".encode('ascii'))
            time.sleep(0.5)
        
        print(f"[+] Fault injected successfully on {DEVICE_NAME}!")
        print(f"[!] Troubleshooting Scenario 1: AS Number Mismatch is now active.")
        print(f"[!] R2 will NOT form adjacency with R1 (AS mismatch)")
        
        tn.close()
        
    except ConnectionRefusedError:
        print(f"[!] Error: Could not connect to {CONSOLE_HOST}:{CONSOLE_PORT}")
        print(f"[!] Make sure GNS3 is running and {DEVICE_NAME} is started.")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("="*60)
    print("Fault Injection: AS Number Mismatch")
    print("="*60)
    inject_fault()
    print("="*60)
