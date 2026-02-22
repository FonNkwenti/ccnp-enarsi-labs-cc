import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../common/tools')))
from fault_utils import FaultInjector

def inject():
    """Stub Flag Mismatch: R3 configured for stub, R7 not."""
    commands_r3 = [
        "router ospf 1",
        " area 37 stub no-summary"
    ]
    commands_r7 = [
        "router ospf 1",
        " no area 37 stub"
    ]
    injector = FaultInjector()
    injector.execute_commands(5003, commands_r3, "R3 Stub Configuration")
    injector.execute_commands(5007, commands_r7, "R7 Normal Area Configuration")
    print("\nScenario 1 fault injected successfully (Stub Mismatch).")
    print("Check the workbook for troubleshooting mission.")

if __name__ == "__main__":
    inject()
