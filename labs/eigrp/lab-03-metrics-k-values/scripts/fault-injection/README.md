# Fault Injection — EIGRP Lab 03

Each script injects one fault. Work through the corresponding ticket in
`workbook.md` Section 9 before looking at the solution.

## Prerequisites

- GNS3 running with R1, R2, R3 started and reachable via console ports
- Lab loaded to known-good state: `python3 setup_lab.py` (from lab root)
- `pip install netmiko`

## Inject a Fault

```
python3 inject_scenario_01.py   # Ticket 1
python3 inject_scenario_02.py   # Ticket 2
python3 inject_scenario_03.py   # Ticket 3
```

## Restore

```
python3 apply_solution.py
```

Restores all routers to the Lab 03 solution state. Run between tickets.
