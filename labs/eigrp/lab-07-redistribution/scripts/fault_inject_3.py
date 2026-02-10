import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Missing 'subnets' keyword in OSPF"""
    print("Injecting Challenge 3: Missing 'subnets' keyword...")
    commands = [
        "router ospf 1",
        " no redistribute eigrp 100",
        " redistribute eigrp 100"
    ]
    injector = FaultInjector()
    injector.execute_commands(5001, commands, "R1 Missing Subnets Keyword")
    print("\nChallenge 3 injected successfully.")

if __name__ == "__main__":
    inject()