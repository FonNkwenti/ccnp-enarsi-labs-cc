import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """AS Number Mismatch for IPv6 AF on R2"""
    print("Injecting Challenge 2: IPv6 AF AS Mismatch...")
    commands = [
        "router eigrp SKYNET_CORE",
        " no address-family ipv6 autonomous-system 100",
        " address-family ipv6 autonomous-system 666",
        "  topology base",
        "  exit-af-topology"
    ]
    injector = FaultInjector()
    injector.execute_commands(5002, commands, "R2 IPv6 AS 666")
    print("\nChallenge 2 injected successfully.")

if __name__ == "__main__":
    inject()