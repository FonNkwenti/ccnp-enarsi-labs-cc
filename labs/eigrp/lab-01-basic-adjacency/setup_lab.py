import socket
import sys
import time
import os

class LabSetup:
    def __init__(self, devices):
        self.devices = devices  # List of (name, port, config_path)

    def push_config(self, host, port, config_file):
        print(f"Connecting to {host}:{port}...")
        try:
            tn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tn.settimeout(5)
            tn.connect((host, port))
            
            # Ensure we are at a prompt
            tn.sendall(b"\r\n")
            time.sleep(1)
            
            # Enter configuration mode
            tn.sendall(b"enable\r\n")
            tn.sendall(b"configure terminal\r\n")
            
            if not os.path.exists(config_file):
                print(f"  Error: Config file {config_file} not found.")
                return False

            with open(config_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('!'):
                        tn.sendall(line.encode('ascii') + b"\r\n")
                        # Small delay to prevent buffer overflow
                        time.sleep(0.1)
            
            tn.sendall(b"end\r\n")
            tn.sendall(b"write memory\r\n")
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
            config_path = os.path.join(os.path.dirname(__file__), config)
            self.push_config("127.0.0.1", port, config_path)
        print("Lab Setup Complete.")

if __name__ == "__main__":
    # Device Mapping for Lab 01
    devices = [
        ("R1", 5001, "initial-configs/R1.cfg"),
        ("R2", 5002, "initial-configs/R2.cfg"),
        ("R3", 5003, "initial-configs/R3.cfg")
    ]
    setup = LabSetup(devices)
    setup.run()
