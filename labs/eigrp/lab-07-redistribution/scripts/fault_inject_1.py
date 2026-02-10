import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Missing Seed Metric for EIGRP"""
    print("Injecting Challenge 1: Missing EIGRP Seed Metric...")
    commands = [
        "router eigrp 100",
        " no redistribute ospf 1",
        " redistribute ospf 1"
    ]
    injector = FaultInjector()
    injector.execute_commands(5001, commands, "R1 Missing EIGRP Metric")
    print("\nChallenge 1 injected successfully.")

if __name__ == "__main__":
    inject()