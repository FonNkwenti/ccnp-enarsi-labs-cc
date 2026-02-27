# Fault Injection — EIGRP Lab 06

Each script injects one fault. Work through the corresponding ticket in
`workbook.md` Section 9 before looking at the solution.

## Prerequisites

- GNS3 topology running with R1, R2, R3, and R4 powered on
- `setup_lab.py` (in the lab root) run successfully to establish the known-good state
- Netmiko installed: `pip install netmiko`
- All routers accessible on 127.0.0.1 via console ports 5001–5004

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

Run `apply_solution.py` between tickets to return to the known-good state before
injecting the next fault. Always restore before ending your lab session.
