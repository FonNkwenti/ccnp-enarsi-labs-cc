#!/usr/bin/env python3
"""
Fault Injection Script Template: Missing Network Statement

Injects: Missing EIGRP Network Advertisement
Target Device: R1
Fault Type: Route Advertisement Error

This script connects to R1 via console and removes the network statement
for the Loopback0 interface, preventing it from being advertised to neighbors.
"""

import socket
import time
import sys

# Device Configuration
DEVICE_NAME = "R1"
CONSOLE_HOST = "127.0.0.1"
CONSOLE_PORT = 5001
TIMEOUT = 10

# Fault Configuration Commands
FAULT_COMMANDS = [
    "configure terminal",
    "router eigrp 100",
    "no network 1.1.1.1 0.0.0.0",
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
        print(f"[*] Removing Loopback0 network statement (FAULT)")
        for cmd in FAULT_COMMANDS:
            print(f"    {cmd}")
            tn.sendall(f"{cmd}\n".encode('ascii'))
            time.sleep(0.5)
        
        print(f"[+] Fault injected successfully on {DEVICE_NAME}!")
        print(f"[!] Troubleshooting Scenario 3: Missing Network Statement is now active.")
        print(f"[!] R1's Loopback0 (1.1.1.1/32) will NOT be advertised to neighbors")
        
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
    print("Fault Injection: Missing Network Statement")
    print("="*60)
    inject_fault()
    print("="*60)
