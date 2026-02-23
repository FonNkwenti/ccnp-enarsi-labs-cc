#!/usr/bin/env python3
"""Restore all routers to known-good (solutions/) state"""
from netmiko import ConnectHandler

devices = [
    {"name": "R1", "host": "127.0.0.1", "port": 5001},
    {"name": "R2", "host": "127.0.0.1", "port": 5002},
    {"name": "R3", "host": "127.0.0.1", "port": 5003},
]

def main():
    for device in devices:
        print(f"\\n[*] Restoring {device['name']} to known-good state...")

        try:
            conn = ConnectHandler(
                device_type="cisco_ios_telnet",
                host=device["host"],
                port=device["port"],
                timeout=15,
                global_delay_factor=2,
            )

            # Load solution config
            config_file = f"../solutions/{device['name']}.cfg"
            with open(config_file, "r") as f:
                commands = f.read().strip().split("\\n")

            commands = [cmd.strip() for cmd in commands if cmd.strip() and not cmd.strip().startswith("!")]

            # Send commands
            output = conn.send_config_set(commands, exit_config_mode=True)
            print(f"[+] {device['name']} restored")

            conn.disconnect()

        except Exception as e:
            print(f"[-] Error on {device['name']}: {e}")
            return False

    print("\\n[+] All routers restored to solutions state!")
    return True

if __name__ == "__main__":
    main()
