# Fault Injection — EIGRP Lab 08

Each script injects one fault. Work through the corresponding ticket in
`workbook.md` Section 9 before looking at the solution.

## Prerequisites

- GNS3 project must be running with all devices started
- All devices accessible via their console ports
- Python 3.x installed
- `netmiko` library installed (`pip install netmiko`)

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
