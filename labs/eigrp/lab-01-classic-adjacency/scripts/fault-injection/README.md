# Lab 01 — Fault Injection Scripts

Operator reference for the three troubleshooting scenarios in Lab 01, Section 9.

## Prerequisites

```bash
pip install netmiko
```

GNS3 must be running with R1, R2, R3 all powered on. Console ports: R1=5001, R2=5002, R3=5003 (Telnet to 127.0.0.1).

## Scripts

| Script | Ticket | Fault Injected | Affected Router |
|--------|--------|----------------|-----------------|
| `inject_scenario_01.py` | 09-1: Branch A Isolated | EIGRP AS 200 configured instead of AS 100 | R2 |
| `inject_scenario_02.py` | 09-2: R1 Cannot Reach Branch A | `passive-interface FastEthernet0/0` under EIGRP | R1 |
| `inject_scenario_03.py` | 09-3: R3 Loopback Unreachable | Missing `network 10.0.0.3 0.0.0.0` statement | R3 |
| `apply_solution.py` | — | Restores all routers to correct EIGRP AS 100 state | R1, R2, R3 |

## Usage

```bash
# Inject one fault at a time
python3 inject_scenario_01.py

# Student troubleshoots... then restore correct state
python3 apply_solution.py

# Proceed to next scenario
python3 inject_scenario_02.py
```

## Notes

- Run `apply_solution.py` between scenarios to ensure a clean starting state
- Fault scripts are idempotent — safe to run multiple times
- Do not share this README with students before they attempt the troubleshooting tickets
