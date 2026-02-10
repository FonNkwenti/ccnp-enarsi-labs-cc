import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Disable IPv6 on Tunnel interface on R6"""
    print("Injecting Challenge 3: Disable IPv6 on Tunnel...")
    commands = [
        "interface Tunnel8",
        " no ipv6 enable",
        " no ipv6 address 2001:DB8:ACAD:16::2/64"
    ]
    injector = FaultInjector()
    injector.execute_commands(5006, commands, "R6 Tunnel IPv6 Disabled")
    print("\nChallenge 3 injected successfully.")

if __name__ == "__main__":
    inject()