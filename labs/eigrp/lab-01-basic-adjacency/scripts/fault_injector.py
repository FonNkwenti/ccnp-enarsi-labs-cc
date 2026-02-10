import sys
import os
import argparse

# Add common tools to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../common/tools')))
from fault_utils import FaultInjector

def inject_challenge_1(injector):
    """AS Number Mismatch on R2"""
    print("Injecting Challenge 1: AS Number Mismatch...")
    commands = [
        "no router eigrp 100",
        "router eigrp 200",
        " network 2.2.2.2 0.0.0.0",
        " network 10.0.12.0 0.0.0.3",
        " network 10.0.23.0 0.0.0.3"
    ]
    injector.execute_commands(5002, commands, "R2 AS Mismatch")

def inject_challenge_2(injector):
    """K-Value Mismatch on R3"""
    print("Injecting Challenge 2: K-Value Mismatch...")
    commands = [
        "router eigrp 100",
        " metric weights 0 1 1 1 1 1"
    ]
    injector.execute_commands(5003, commands, "R3 K-Value Mismatch")

def inject_challenge_3(injector):
    """Passive Interface on transit link R2 Fa0/1"""
    print("Injecting Challenge 3: Passive Transit Interface...")
    commands = [
        "router eigrp 100",
        " passive-interface FastEthernet0/1"
    ]
    injector.execute_commands(5002, commands, "R2 Passive Fa0/1")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fault Injector for EIGRP Lab 01")
    parser.add_argument("challenge", type=int, choices=[1, 2, 3], help="Challenge number to inject")
    args = parser.parse_args()

    injector = FaultInjector()
    
    if args.challenge == 1:
        inject_challenge_1(injector)
    elif args.challenge == 2:
        inject_challenge_2(injector)
    elif args.challenge == 3:
        inject_challenge_3(injector)
    
    print(f"\nChallenge {args.challenge} injected successfully.")