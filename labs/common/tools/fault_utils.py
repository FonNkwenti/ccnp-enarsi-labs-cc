import socket
import time
import sys

class FaultInjector:
    def __init__(self, host="127.0.0.1"):
        self.host = host

    def execute_commands(self, port, commands, description="Injecting fault"):
        """
        Connects to a GNS3 console via raw socket and executes IOS
        configuration commands.  Identical pattern to refresh_lab.py.
        """
        try:
            tn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tn.settimeout(5)
            tn.connect((self.host, port))
            tn.sendall(b"\r\n")
            time.sleep(0.5)
            tn.sendall(b"enable\r\n")
            tn.sendall(b"configure terminal\r\n")

            for cmd in commands:
                if cmd.strip():
                    tn.sendall(cmd.strip().encode('ascii') + b"\r\n")
                    time.sleep(0.1)

            tn.sendall(b"end\r\n")
            tn.close()
            return True
        except Exception as e:
            print(f"  Error: {e}")
            return False

if __name__ == "__main__":
    injector = FaultInjector()
    print("FaultInjector utility loaded.")
