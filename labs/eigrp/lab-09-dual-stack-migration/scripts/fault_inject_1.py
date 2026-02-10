import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Disable IPv6 Unicast Routing on R2"""
    print("Injecting Challenge 1: Disable IPv6 Unicast Routing...")
    commands = [
        "no ipv6 unicast-routing"
    ]
    injector = FaultInjector()
    injector.execute_commands(5002, commands, "R2 IPv6 Unicast Disabled")
    print("\nChallenge 1 injected successfully.")

if __name__ == "__main__":
    inject()