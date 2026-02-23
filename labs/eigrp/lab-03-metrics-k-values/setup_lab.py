#!/usr/bin/env python3
"""
Lab 03 Setup: EIGRP Metrics & K-Values
Loads initial-configs to all routers and verifies connectivity.
"""

from netmiko import ConnectHandler
import sys
import time

ROUTERS = [
    {"host": "localhost", "port": 5001, "device_type": "cisco_ios_telnet", "username": "", "password": "", "secret": "", "name": "R1"},
    {"host": "localhost", "port": 5002, "device_type": "cisco_ios_telnet", "username": "", "password": "", "secret": "", "name": "R2"},
    {"host": "localhost", "port": 5003, "device_type": "cisco_ios_telnet", "username": "", "password": "", "secret": "", "name": "R3"},
]

CONFIG_DIR = "initial-configs"

def load_config(router_info):
    """Load config file to router."""
    try:
        net_connect = ConnectHandler(**router_info)
        router_name = router_info["name"]
        config_file = f"{CONFIG_DIR}/{router_name}.cfg"

        print(f"[*] Loading {router_name} config from {config_file}...")
        with open(config_file, "r") as f:
            commands = f.read().split("\\n")
            # Filter out empty lines and ! comments
            commands = [cmd.strip() for cmd in commands if cmd.strip() and not cmd.startswith("!")]
            net_connect.send_config_set(commands)

        net_connect.disconnect()
        print(f"[+] {router_name} configured successfully\\n")
        return True
    except Exception as e:
        print(f"[-] Error configuring {router_name}: {e}\\n")
        return False

def verify_neighbors():
    """Verify EIGRP neighbors are formed."""
    try:
        net_connect = ConnectHandler(host="localhost", port=5001, device_type="cisco_ios_telnet", username="", password="", secret="")
        time.sleep(2)  # Allow time for adjacencies to form

        output = net_connect.send_command("show ip eigrp neighbors")
        net_connect.disconnect()

        if "10.0.0.2" in output and "10.0.0.3" in output:
            print("[+] EIGRP neighbors verified on R1")
            return True
        else:
            print("[-] EIGRP neighbors not fully formed")
            return False
    except Exception as e:
        print(f"[-] Error verifying neighbors: {e}")
        return False

if __name__ == "__main__":
    print("\\n=== Lab 03: EIGRP Metrics & K-Values Setup ===\\n")

    success_count = 0
    for router in ROUTERS:
        if load_config(router):
            success_count += 1

    print(f"\\n[*] Configured {success_count}/{len(ROUTERS)} routers")

    if success_count == len(ROUTERS):
        print("\\n[*] Waiting for EIGRP adjacencies to form...")
        time.sleep(5)
        if verify_neighbors():
            print("\\n[+] Lab setup complete!\\n")
            sys.exit(0)
        else:
            print("\\n[!] Setup complete but neighbors not verified\\n")
            sys.exit(1)
    else:
        print("\\n[-] Setup incomplete\\n")
        sys.exit(1)
