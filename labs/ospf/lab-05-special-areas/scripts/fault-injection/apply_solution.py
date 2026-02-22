import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../common/tools')))
from fault_utils import FaultInjector

def apply():
    """Apply solution for Scenario 1 (Totally Stubby)"""
    commands_r3 = [
        "router ospf 1",
        " area 37 stub no-summary"
    ]
    commands_r7 = [
        "router ospf 1",
        " area 37 stub"
    ]
    injector = FaultInjector()
    injector.execute_commands(5003, commands_r3, "Restore R3 Solution")
    injector.execute_commands(5007, commands_r7, "Restore R7 Solution")
    print("\nSolution applied successfully. Area 37 is now Totally Stubby.")

if __name__ == "__main__":
    apply()
