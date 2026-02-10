import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """MTU Mismatch / Too Large on R6"""
    print("Injecting Challenge 2: MTU Issues...")
    commands = [
        "interface Tunnel8",
        " no ip mtu",
        " ip mtu 1500"
    ]
    injector = FaultInjector()
    injector.execute_commands(5006, commands, "R6 Large MTU")
    print("\nChallenge 2 injected successfully.")

if __name__ == "__main__":
    inject()