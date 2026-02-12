import telnetlib
import sys
import time
import os

class LabSetup:
    def __init__(self, devices):
        self.devices = devices  # List of (name, port, config_path)

    def push_config(self, host, port, config_file):
        print(f"Connecting to {host}:{port}...")
        try:
            tn = telnetlib.Telnet(host, port, timeout=5)
            
            # Ensure we are at a prompt
            tn.write(b"\r\n")
            time.sleep(1)
            
            # Enter configuration mode
            tn.write(b"enable\r\n")
            tn.write(b"configure terminal\r\n")
            
            if not os.path.exists(config_file):
                print(f"  Error: Config file {config_file} not found.")
                return False

            with open(config_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('!'):
                        tn.write(line.encode('ascii') + b"\r\n")
                        # Small delay to prevent buffer overflow
                        time.sleep(0.1)
            
            tn.write(b"end\r\n")
            tn.write(b"write memory\r\n")
            print(f"  Successfully loaded {config_file}")
            tn.close()
            return True
        except Exception as e:
            print(f"  Failed to connect or push config: {e}")
            return False

    def run(self):
        print("Starting Lab Setup Automation...")
        for name, port, config in self.devices:
            print(f"--- Setting up {name} ---")
            self.push_config("127.0.0.1", port, config)
        print("Lab Setup Complete.")

# --- Device Mapping Area ---
# This part will be generated dynamically for each lab
