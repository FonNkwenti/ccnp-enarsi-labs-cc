#!/usr/bin/env python3
"""
Lab 02 Setup: Deploy initial configs to all routers via Netmiko telnet
"""
from netmiko import ConnectHandler

devices = [
    {"name": "R1", "host": "127.0.0.1", "port": 5001},
    {"name": "R2", "host": "127.0.0.1", "port": 5002},
    {"name": "R3", "host": "127.0.0.1", "port": 5003},
]

def main():
    for device in devices:
        print(f"\\n[*] Connecting to {device['name']} ({device['host']}:{device['port']})...")

        try:
            conn = ConnectHandler(
                device_type="cisco_ios_telnet",
                host=device["host"],
                port=device["port"],
                username="",
                password="",
                secret="",
                timeout=15,
                global_delay_factor=2,
            )

            print(f"[+] Connected to {device['name']}")

            # Load config from file
            config_file = f"initial-configs/{device['name']}.cfg"
            with open(config_file, "r") as f:
                commands = f.read().strip().split("\\n")

            # Filter out empty lines and comments
            commands = [cmd.strip() for cmd in commands if cmd.strip() and not cmd.strip().startswith("!")]

            print(f"[*] Sending {len(commands)} commands to {device['name']}...")
            output = conn.send_config_set(commands, exit_config_mode=True)

            print(f"[+] Config applied to {device['name']}")
            conn.disconnect()

        except Exception as e:
            print(f"[-] Error on {device['name']}: {e}")
            return False

    print("\\n[+] All routers configured successfully!")
    return True

if __name__ == "__main__":
    main()
