import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Destination Unreachable (Physical Link Down) on R1"""
    print("Injecting Challenge 3: Destination Unreachable...")
    commands = [
        "interface GigabitEthernet3/0",
        " shutdown"
    ]
    injector = FaultInjector()
    injector.execute_commands(5001, commands, "R1 Gi3/0 Shutdown")
    print("\nChallenge 3 injected successfully.")

if __name__ == "__main__":
    inject()