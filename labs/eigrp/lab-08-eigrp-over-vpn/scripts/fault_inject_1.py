import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Recursive Routing on R1"""
    print("Injecting Challenge 1: Recursive Routing...")
    commands = [
        "router eigrp 100",
        " network 10.0.16.0 0.0.0.3"
    ]
    injector = FaultInjector()
    injector.execute_commands(5001, commands, "R1 Recursive Routing")
    print("\nChallenge 1 injected successfully.")

if __name__ == "__main__":
    inject()