# Fault Injection — EIGRP Lab 01

Each script injects one fault into the live GNS3 topology. Work through the corresponding ticket in `workbook.md` Section 8 before looking at the solution.

## Prerequisites

- GNS3 running with R1, R2, R3 powered on
- `python3 setup_lab.py` already run (initial configs loaded)
- `pip install netmiko`

## Inject a Fault

Run from the `scripts/fault-injection/` directory:

```bash
python3 inject_scenario_01.py   # Ticket 1
python3 inject_scenario_02.py   # Ticket 2
python3 inject_scenario_03.py   # Ticket 3
```

Troubleshoot using `workbook.md` Section 8. Do not open the inject script until after you have resolved the fault.

## Restore

After completing any ticket, restore all devices to the correct configuration:

```bash
python3 apply_solution.py
```
