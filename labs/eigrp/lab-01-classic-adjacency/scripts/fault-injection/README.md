# Fault Injection Scripts — EIGRP Lab 01

## Prerequisites

- GNS3 running with R1, R2, R3 powered on
- `python3 setup_lab.py` already executed (initial configs loaded)
- `pip install netmiko`

## Available Scenarios

### Scenario 01 — AS Number Mismatch
**Target:** R2
**Fault:** R2 joins EIGRP AS 200 instead of AS 100
**Symptom:** R2 has no EIGRP neighbors; R1 and R3 lose routes to R2's subnets
**Key command to check:** `show ip eigrp neighbors` on R2

```bash
python3 inject_scenario_01.py
```

---

### Scenario 02 — Passive Interface
**Target:** R1
**Fault:** R1 FastEthernet0/0 is made passive — no EIGRP Hellos sent/received on R1-R2 link
**Symptom:** R1-R2 adjacency drops; R2 cannot reach R3 via R1
**Key command to check:** `show ip eigrp interfaces` on R1

```bash
python3 inject_scenario_02.py
```

---

### Scenario 03 — Missing Network Statement
**Target:** R3
**Fault:** R3 removes the `network 10.23.0.0 0.0.0.3` statement — Fa0/1 subnet stops being advertised
**Symptom:** R3-R2 adjacency drops; 10.23.0.0/30 disappears from R1 and R2 routing tables
**Key command to check:** `show run | section eigrp` on R3

```bash
python3 inject_scenario_03.py
```

---

## Restoring the Lab

After completing any scenario, restore all devices to the correct configuration:

```bash
python3 apply_solution.py
```

This pushes `solutions/[Device].cfg` to all routers and saves the config.
