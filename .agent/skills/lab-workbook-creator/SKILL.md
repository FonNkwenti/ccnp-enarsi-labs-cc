---
name: lab-workbook-creator
description: Creates a complete CCNP ENARSI lab workbook, initial-configs, solutions, topology diagram, and setup_lab.py automation script for a single lab. Use when the user asks to "create a lab", "generate lab N", "build [technology] lab", "write a workbook", or when chapter-builder invokes it for each lab in a sequence.
---

# Lab Workbook Creator Skill

Converts a lab topic entry from `baseline.yaml` into a full DeepSeek Standard lab package. Prioritises theoretical context, copy-pasteable Cisco IOS configurations, and GNS3 automation scripts.

-# Instructions

--# Step 1: Read Inputs

Before generating anything, read:
1. `labs/[chapter]/baseline.yaml` — active devices, IPs, console ports, lab objectives
2. Previous lab's `solutions/` (if this is not Lab 01) — becomes this lab's `initial-configs/`
3. `specs/[chapter]/chapter-spec.md` — exam bullet context for the lab's objectives

Identify which devices are active for this lab number from `baseline.yaml labs[N].devices`.

--# Step 2: Generate workbook.md

Write a complete workbook with all required sections:

1. **Concepts & Skills Covered** — exam blueprint bullets this lab addresses
2. **Topology & Scenario** — enterprise narrative framing the lab challenge
3. **Hardware & Environment Specifications** — cabling table, Console Access Table
4. **Base Configuration** — what is pre-configured in `initial-configs/`
5. **Lab Challenge: Core Implementation** — step-by-step objectives for the student
6. **Verification & Analysis** — expected `show` command outputs per objective
7. **Verification Cheatsheet** — quick-reference commands for the entire lab
8. **Solutions (Spoiler Alert!)** — complete solutions wrapped in `<details>` blocks (see format below)
9. **Lab Completion Checklist** — student self-assessment checkboxes
10. **Automated Fault Injection (Optional)** — instructions for fault-injection scripts

**Solutions section format (required):**
```markdown
## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these steps first!

### Objective 1: [Title]

<details>
<summary>Click to view [Device] Configuration</summary>

```bash
! R1
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  ...
```
</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
show ip eigrp neighbors
show ip route eigrp
```
</details>
```

**ASCII Topology Diagram standard (required in Section 2):**

Use Unicode box-drawing characters. Every diagram must include:
- Device box: `┌─┐│└─┘` with hostname, role, and Loopback0 IP inside
- Interface name **and** full IP/mask labeled on each link segment (local side above, remote side below the gap)
- Subnet label on horizontal bottom links
- Do NOT use `/`, `\`, or plain `-` lines — use `│` for vertical links and `─` inside boxes only

Chain (linear) example:
```
                    ┌─────────────────┐
                    │       R1        │
                    │   (Hub Router)  │
                    │ Lo0: 10.0.0.1   │
                    └───────┬─────────┘
                            │ Fa0/0
                            │ 10.12.0.1/30
                            │
                            │ 10.12.0.2/30
                            │ Fa0/0
                    ┌───────┴─────────┐
                    │       R2        │
                    │ (Branch Router) │
                    │ Lo0: 10.0.0.2   │
                    └─────────────────┘
```

Triangle (hub + two branches) example:
```
              ┌─────────────────────────┐
              │           R1            │
              │      (Hub / Core)       │
              │   Lo0: 10.0.0.1/32      │
              └──────┬───────────┬──────┘
           Fa0/0     │           │     Fa1/0
     10.12.0.1/30    │           │   10.13.0.1/30
                     │           │
     10.12.0.2/30    │           │   10.13.0.2/30
           Fa0/0     │           │     Fa0/0
     ┌───────────────┘           └───────────────┐
     │                                           │
┌────┴──────────────┐           ┌────────────────┴────┐
│       R2          │           │       R3            │
│   (Branch A)      │           │   (Branch B)        │
│ Lo0: 10.0.0.2/32  │           │ Lo0: 10.0.0.3/32    │
└─────────┬─────────┘           └─────────┬───────────┘
      Fa0/1│                              │Fa0/1
10.23.0.1/30│                            │10.23.0.2/30
            └────────────────────────────┘
                      10.23.0.0/30
```

**Console Access Table format (required in Section 3):**

| Device | Port | Connection Command |
|--------|------|--------------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |

--# Step 3: Generate initial-configs/

- **Lab 01:** Generate base IP addressing from `baseline.yaml core_topology` (IP config only — no routing protocol config).
- **Lab N (N > 1):** Copy exactly from Lab (N-1) `solutions/`. Do not modify.
- One `.cfg` file per active device, named `[Device].cfg`.

--# Step 4: Generate solutions/

Complete IOS configurations for every active device, implementing all lab objectives. One `.cfg` file per device.

--# Step 5: Generate topology.drawio

Create the topology diagram following the drawio Visual Style Guide. Invoke the `drawio` skill to ensure compliance:
- White connection lines (`strokeColor=#FFFFFF`)
- Device labels on the empty side of the icon
- IP last octet labels near each interface
- Title at top center, legend box at bottom-right

--# Step 6: Generate setup_lab.py

Use `assets/setup_lab_template.py` as the base template. Customise it for this lab's active devices and console ports from `baseline.yaml`.

The script must:
1. Use `device_type='cisco_ios_telnet'` to connect via console ports
2. Loop through each active device
3. Load the corresponding `initial-configs/[Device].cfg`
4. Log progress clearly per device

--# Step 7: Invoke fault-injector skill

After generating the workbook, invoke the `fault-injector` skill to create `scripts/fault-injection/` scripts based on the troubleshooting scenarios in the workbook.

Use `assets/troubleshooting_scenarios_template.md` as the template for Section 8 troubleshooting content.

-# Common Issues

--# baseline.yaml not found
- **Cause:** Chapter has not been planned yet.
- **Solution:** Stop. Ask the user to run the `chapter-topics` skill first to generate `labs/[chapter]/baseline.yaml`.

--# No previous lab solutions to chain from (Lab N > 1)
- **Cause:** Lab (N-1) has not been generated yet.
- **Solution:** Stop. Labs must be generated in sequence. Generate Lab (N-1) first, or ask the user whether to generate from the baseline instead (treating it as Lab 01 style).

--# Device in baseline.yaml has no console port defined
- **Cause:** Incomplete baseline.yaml.
- **Solution:** Fall back to default convention (R1=5001, RN=500N). Flag the gap to the user.

--# Solutions section incomplete
- **Cause:** Not all lab objectives have a corresponding solution block.
- **Solution:** Every objective listed in Section 5 (Lab Challenge) must have a `<details>` solution block in Section 8. Go back and complete before finishing.

-# Examples

User: "Generate EIGRP Lab 03 for the ENARSI series."

Actions:
1. Read `labs/eigrp/baseline.yaml` — identify Lab 03 devices, objectives, console ports.
2. Copy `labs/eigrp/lab-02-[name]/solutions/` as `initial-configs/` for Lab 03.
3. Write `workbook.md` with all 10 required sections.
4. Generate `initial-configs/`, `solutions/`, `topology.drawio`, `setup_lab.py`.
5. Invoke `drawio` skill to validate topology diagram style.
6. Invoke `fault-injector` skill to generate `scripts/fault-injection/`.
