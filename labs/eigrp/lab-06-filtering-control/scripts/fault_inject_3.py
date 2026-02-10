import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Broad Access-List Filtering on R3"""
    print("Injecting Challenge 3: Broad Access-List Filtering...")
    commands = [
        "no access-list 66",
        "access-list 66 deny 0.0.0.0 255.255.255.255"
    ]
    injector = FaultInjector()
    injector.execute_commands(5003, commands, "R3 Block All to R5")
    print("\nChallenge 3 injected successfully.")

if __name__ == "__main__":
    inject()