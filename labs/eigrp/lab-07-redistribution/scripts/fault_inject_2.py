import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Restrictive Tagging on OSPF"""
    print("Injecting Challenge 2: Restrictive Tagging...")
    commands = [
        "route-map EIGRP_TO_OSPF deny 5",
        " match tag 222",
        "route-map EIGRP_TO_OSPF permit 10",
        " set tag 222"
    ]
    injector = FaultInjector()
    injector.execute_commands(5001, commands, "R1 Restrictive OSPF Tagging")
    print("\nChallenge 2 injected successfully.")

if __name__ == "__main__":
    inject()