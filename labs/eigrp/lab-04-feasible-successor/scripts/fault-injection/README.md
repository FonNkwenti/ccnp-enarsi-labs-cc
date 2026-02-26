# Fault Injection — EIGRP Lab 04

Each script injects one fault. Work through the corresponding ticket in
`workbook.md` Section 9 before looking at the solution.

## Prerequisites

- GNS3 running with R1, R2, R3 started and reachable on console ports 5001–5003
- `pip install netmiko`
- Run `python3 setup_lab.py` from the lab root to reset to initial-configs first

## Inject a Fault

```bash
python3 inject_scenario_01.py   # Ticket 1
python3 inject_scenario_02.py   # Ticket 2
python3 inject_scenario_03.py   # Ticket 3
```

## Restore

```bash
python3 apply_solution.py
```

Restores all routers to the Lab 04 solution state. Run this between tickets
or after completing a troubleshooting session.
