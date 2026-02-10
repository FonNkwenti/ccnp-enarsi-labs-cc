import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Implicit Deny on R2 Route-Map"""
    print("Injecting Challenge 2: Route-Map Implicit Deny...")
    commands = [
        "no route-map RM_FILTER_R3 permit 20",
        "route-map RM_FILTER_R3 deny 10",
        " match ip address prefix-list R1_LOOP"
    ]
    injector = FaultInjector()
    injector.execute_commands(5002, commands, "R2 Route-Map Deny Only")
    print("\nChallenge 2 injected successfully.")

if __name__ == "__main__":
    inject()