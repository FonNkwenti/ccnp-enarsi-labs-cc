# Fault Injection — EIGRP Lab 07

Each script injects one fault. Work through the corresponding ticket in
`workbook.md` Section 9 before looking at the solution.

## Prerequisites

- GNS3 running with R1–R4 started and in known-good state
- `python3 setup_lab.py` run from the lab root (loads initial-configs)
- Solution configuration applied: `python3 apply_solution.py`
- `pip install netmiko`

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

Run `apply_solution.py` between each ticket to reset all routers to the
lab-07 known-good solution state before injecting the next fault.
