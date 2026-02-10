import telnetlib
import time
import sys

class FaultInjector:
    def __init__(self, host="127.0.0.1"):
        self.host = host

    def execute_commands(self, port, commands, description="Injecting fault"):
        """
        Connects via Telnet and executes a list of configuration commands.
        """
        print(f"[{description}] Connecting to {self.host}:{port}...")
        try:
            tn = telnetlib.Telnet(self.host, port, timeout=5)
            
            # Ensure prompt
            tn.write(b"\n")
            time.sleep(1)
            
            tn.write(b"enable\n")
            tn.write(b"configure terminal\n")
            time.sleep(0.5)

            for cmd in commands:
                print(f"  Executing: {cmd}")
                tn.write(cmd.encode('ascii') + b"\n")
                time.sleep(0.2)
            
            tn.write(b"end\n")
            tn.write(b"exit\n")
            tn.close()
            print(f"  Successfully executed commands.")
            return True
        except Exception as e:
            print(f"  Error: {e}")
            return False

if __name__ == "__main__":
    # Example usage (dry run check)
    injector = FaultInjector()
    print("FaultInjector utility loaded.")