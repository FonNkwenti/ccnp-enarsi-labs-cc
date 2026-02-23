# Fault Injection — EIGRP Lab 02

Each script injects one fault. Work through the corresponding ticket in `../../workbook.md` Section 9 before looking at the solution.

## Prerequisites

- Lab setup running: `python3 ../../setup_lab.py`
- Routers accessible on localhost:5001-5003 (telnet)
- Python 3 with netmiko installed

## Inject a Fault

```bash
python3 inject_scenario_01.py   # Ticket 1
python3 inject_scenario_02.py   # Ticket 2
python3 inject_scenario_03.py   # Ticket 3
python3 inject_scenario_04.py   # Ticket 4
python3 inject_scenario_05.py   # Ticket 5
```

## Restore

```bash
python3 apply_solution.py
```

All routers will be restored to the known-good (solutions/) state.
