Generate fault injection scripts for troubleshooting scenarios in: $ARGUMENTS

## Purpose

Create automated Python scripts that inject the troubleshooting scenarios defined in a lab workbook into the live GNS3 environment. Enables exam-style "find the fault" practice without manual misconfiguration.

## Workflow

Use the `fault-injector` skill. Provide the lab path as the argument (e.g., `labs/eigrp/lab-03-named-mode`).

The skill will:

1. Read `workbook.md` — extract Console Access Table and Section 9 troubleshooting scenarios (minimum 3)
2. For each scenario, generate `scripts/fault-injection/inject_scenario_0N.py`
3. Generate `scripts/fault-injection/apply_solution.py` — restores all devices to correct config
4. Generate `scripts/fault-injection/README.md` — usage instructions per scenario

## Script requirements

- Netmiko `ConnectHandler` with `device_type="cisco_ios_telnet"`
- Connect to `127.0.0.1:<console_port>` from the Console Access Table
- `send_config_set()` to inject misconfiguration commands
- Clear progress output: connecting → injecting → done
- Graceful error handling with non-zero exit on failure
- Scripts must be idempotent (safe to run multiple times)

## Arguments format

Provide the lab path: `labs/<chapter>/lab-NN-<slug>`

## After generation

Update `memory/progress.md` — set fault-injection status for this lab to Complete if scripts were generated successfully.
