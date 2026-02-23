Create a detailed lab workbook and all supporting artifacts for: $ARGUMENTS

## Pre-flight checks

1. Read `memory/progress.md` — confirm which lab is next and that Lab (N-1) is Approved
2. Read `labs/<chapter>/baseline.yaml` — devices, IPs, console ports, lab objectives
3. If Lab N > 1: read `labs/<chapter>/lab-(N-1)-*/solutions/` — these become this lab's `initial-configs/`

## Workflow

Use the `lab-workbook-creator` skill. It will generate:

- `labs/<chapter>/lab-NN-<slug>/workbook.md` — full lab guide (10 required sections)
- `labs/<chapter>/lab-NN-<slug>/initial-configs/` — one `.cfg` per active device
- `labs/<chapter>/lab-NN-<slug>/solutions/` — complete solution `.cfg` per device
- `labs/<chapter>/lab-NN-<slug>/topology.drawio` — diagram following drawio Visual Style Guide
- `labs/<chapter>/lab-NN-<slug>/setup_lab.py` — Netmiko automation script (cisco_ios_telnet)

After the workbook is generated, the `fault-injector` skill runs automatically and adds:

- `labs/<chapter>/lab-NN-<slug>/scripts/fault-injection/inject_scenario_0N.py`
- `labs/<chapter>/lab-NN-<slug>/scripts/fault-injection/apply_solution.py`
- `labs/<chapter>/lab-NN-<slug>/scripts/fault-injection/README.md`

## Rules

- **One lab per session** — stop after this lab and wait for review
- **Never remove commands between labs** — initial-configs must include everything from the previous lab's solutions
- Solution configs must be wrapped in `<details>` spoiler blocks in the workbook
- Console ports follow R1=5001, R2=5002, … RN=500N convention

## After generation

Update `memory/progress.md`:
- Set this lab's status to **Review Needed**
- Set "Active Work → Last completed lab" to this lab number
- Set "Next action" to: "Review lab-NN — approve before generating lab-N+1"
