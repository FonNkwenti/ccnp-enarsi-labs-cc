Generate a comprehensive lab topics blueprint and baseline topology for: $ARGUMENTS

## Purpose

Create the strategic plan for a new ENARSI chapter, ensuring all 300-410 exam objectives are covered through a progressive series of labs.

## Pre-flight checks

1. Read `specs/<chapter>/chapter-spec.md` — exam bullets, planned labs, topology notes
2. Read `specs/exam-blueprint.md` — confirm which 300-410 sections this chapter covers
3. Check `memory/progress.md` — confirm this chapter does not already have a baseline.yaml

## Workflow

Use the `chapter-topics-creator` skill. It will generate:

**`labs/<chapter>/baseline.yaml`** with this schema:
```yaml
chapter: <TECHNOLOGY>
version: 1.0
core_topology:
  devices:
    - name: R1
      platform: c7200|c3725
      role: <descriptive role>
      loopback0: <IP/mask>
      console_port: 5001
  links:
    - id: L1
      source: <Device:Interface>
      target: <Device:Interface>
      subnet: <network/mask>
optional_devices:
  - name: R4
    platform: c7200|c3725
    role: <role>
    loopback0: <IP/mask>
    console_port: 5004
    available_from: <lab number>
    purpose: <why needed>
optional_links:
  - id: L3
    source: <Device:Interface>
    target: <Device:Interface>
    subnet: <network/mask>
    available_from: <lab number>
labs:
  - number: 1
    title: <Lab Title>
    difficulty: Foundation|Intermediate|Advanced
    time_minutes: <45-120>
    devices: [R1, R2, R3]
    objectives:
      - <objective 1>
```

## Topology guidelines

- Core devices (3 minimum) for foundation labs
- Optional devices (up to 15 total) for advanced scenarios
- Pre-reserve IPs for ALL potential devices
- Each lab explicitly declares which devices are active
- Platforms: c7200 for hub/ABR/crypto roles, c3725 for branch/spoke roles (see `gns3` skill)
- Interfaces: FastEthernet/GigabitEthernet only — no TenGig or HundredGig
- **Every chapter always ends with Capstone I + Capstone II** — these are the last 2 labs in every series
  - Capstone I: full protocol configuration challenge (clean slate, all blueprint bullets)
  - Capstone II: comprehensive troubleshooting (clean slate, 5+ concurrent faults, all blueprint bullets)
  - Both have `type: capstone_i|capstone_ii` and `clean_slate: true` in baseline.yaml

## After generation

Backfill `specs/<chapter>/chapter-spec.md` with the Generated Plan (topology summary, lab progression table, blueprint coverage table) — see skill Step 4 for format.

Update `memory/progress.md`:
- Add baseline.yaml row for this chapter with status **Approved**
- Set "Active Work → Next action" to: "Generate lab-01 for <chapter>"
