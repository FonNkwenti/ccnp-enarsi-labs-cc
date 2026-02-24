# Lab 02 — Fault Injection Scripts

**Lab:** EIGRP Named Mode & Dual-Stack IPv6 Address Family
**Chapter:** EIGRP | Blueprint: 1.9.a, 1.9.b

---

## Scripts

| Script | Routers Affected | What Is Broken |
|--------|-----------------|----------------|
| `inject_scenario_01.py` | R2 | IPv4 address-family autonomous-system changed to AS 200 |
| `inject_scenario_02.py` | R3 | `ipv6 unicast-routing` removed |
| `inject_scenario_03.py` | R3 | `network 10.0.0.3 0.0.0.0` removed from IPv4 AF |
| `apply_solution.py` | R1, R2, R3 | Restores all routers to correct named-mode dual-stack state |

---

## Usage

### Inject a fault

```bash
# Inject one scenario at a time
python inject_scenario_01.py
python inject_scenario_02.py
python inject_scenario_03.py
```

### Restore to solution state

```bash
python apply_solution.py
```

`apply_solution.py` is idempotent — it is safe to run regardless of which (if any) scenario was injected.

---

## Requirements

```bash
pip install netmiko
```

GNS3 project must be running with:
- R1 console on `127.0.0.1:5001`
- R2 console on `127.0.0.1:5002`
- R3 console on `127.0.0.1:5003`

---

## Notes

- Inject one scenario at a time; run `apply_solution.py` before injecting the next.
- Wait ~15 seconds after injection for EIGRP hold timers to expire.
- Fault descriptions in workbook Section 9 present symptoms only — do not read this file before attempting troubleshooting.
