#!/usr/bin/env python3
"""
Fault Injection Script Template: Passive Interface Misconfiguration

Injects: Passive Interface Default with Wrong Exclusion
Target Device: R3
Fault Type: Interface Configuration Error

This script connects to R3 via console and configures passive-interface default,
then incorrectly excludes Loopback0 instead of the transit interface, preventing
adjacency formation with R2.
"""

import telnetlib
import time
import sys

# Device Configuration
DEVICE_NAME = "R3"
CONSOLE_HOST = "127.0.0.1"
CONSOLE_PORT = 5003
TIMEOUT = 10

# Fault Configuration Commands
FAULT_COMMANDS = [
    "configure terminal",
    "router eigrp 100",
    "passive-interface default",
    "no passive-interface Loopback0",
    "end",
    "write memory",
]

def inject_fault():
    """Connect to device and inject the fault configuration."""
    print(f"[*] Connecting to {DEVICE_NAME} on {CONSOLE_HOST}:{CONSOLE_PORT}...")
    
    try:
        tn = telnetlib.Telnet(CONSOLE_HOST, CONSOLE_PORT, TIMEOUT)
        print(f"[+] Connected to {DEVICE_NAME}")
        
        # Press Enter to get prompt
        tn.write(b"\n")
        time.sleep(1)
        
        # Enter enable mode
        tn.write(b"enable\n")
        time.sleep(1)
        
        # Apply fault commands
        print(f"[*] Injecting fault configuration...")
        print(f"[*] Configuring passive-interface default (FAULT)")
        for cmd in FAULT_COMMANDS:
            print(f"    {cmd}")
            tn.write(f"{cmd}\n".encode('ascii'))
            time.sleep(0.5)
        
        print(f"[+] Fault injected successfully on {DEVICE_NAME}!")
        print(f"[!] Troubleshooting Scenario 2: Passive Interface Misconfiguration is now active.")
        print(f"[!] R3 will NOT form adjacency with R2 (all interfaces passive)")
        
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
    print("Fault Injection: Passive Interface Misconfiguration")
    print("="*60)
    inject_fault()
    print("="*60)
