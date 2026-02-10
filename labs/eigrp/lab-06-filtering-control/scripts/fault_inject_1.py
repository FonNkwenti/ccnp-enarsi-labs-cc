import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Prefix-List Gap on R1"""
    print("Injecting Challenge 1: Prefix-List Next-Hop Gap...")
    commands = [
        "ip prefix-list AUTHORIZED_NETS deny 10.0.12.0/30",
        "ip prefix-list AUTHORIZED_NETS seq 5 permit 2.2.2.2/32",
        "ip prefix-list AUTHORIZED_NETS seq 10 permit 3.3.3.3/32"
    ]
    injector = FaultInjector()
    injector.execute_commands(5001, commands, "R1 Prefix-List Gap")
    print("\nChallenge 1 injected successfully.")

if __name__ == "__main__":
    inject()