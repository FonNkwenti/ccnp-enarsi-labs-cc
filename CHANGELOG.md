# Changelog — CCNP ENARSI Lab Series

All notable changes to the CCNP ENARSI (300-410) lab project are documented here.

---

## [Unreleased]

### Added

#### Memory & Continuity System
- **`memory/progress.md`** — per-chapter lab status tracking table with Active Work indicator
- **`memory/decisions.md`** — append-only design decisions log (5 foundational entries)
- **CLAUDE.md imports** — `@memory/progress.md` and `@memory/decisions.md` auto-loaded into every session

#### EIGRP Chapter (Labs 01–09)
- **`labs/eigrp/baseline.yaml`** — comprehensive 9-lab chapter plan
  - Topology: R1 (c7200 hub) + R2/R3 (c3725 branches) + R4 (optional stub, lab 06+)
  - IPv4 + IPv6 addressing pre-reserved for all devices
  - Labs cover all EIGRP blueprint bullets (1.9.a-f, 1.1-1.3, 1.5)

- **Lab 01: Classic Mode Adjacency** — Foundation (60 min)
  - Full DeepSeek Standard artifact set:
    - `workbook.md` — 10 sections (Concepts, Topology, Hardware, Base Config, Challenge, Verification, Cheatsheet, Solutions, Troubleshooting, Checklist)
    - `initial-configs/` — IP addressing only (R1, R2, R3)
    - `solutions/` — EIGRP AS 100 + network statements (R1, R2, R3)
    - `topology.drawio` — dark background, white links, IP last-octet labels, legend
    - `setup_lab.py` — Netmiko cisco_ios_telnet automation script
  - **Troubleshooting Scenarios** with fault injection:
    - Ticket 1: R2 Reports No EIGRP Neighbors (AS mismatch)
    - Ticket 2: Branch-A Loses Reachability Through the Core (passive interface)
    - Ticket 3: Subnet 10.23.0.0/30 Disappears (missing network statement)
  - **Fault injection scripts** (3 scenarios + restore):
    - `inject_scenario_01.py` — AS number mismatch on R2
    - `inject_scenario_02.py` — passive-interface Fa0/0 on R1
    - `inject_scenario_03.py` — missing network statement on R3
    - `apply_solution.py` — restores all devices from solutions/
    - `README.md` — ops-only usage guide

### Changed

#### Workflow & Process
- **Slash commands** (`.claude/commands/`) — all 6 files rewritten for ENARSI + memory system
  - `create-lab.md` — removed ENCOR/conductor refs, added memory update step
  - `chapter-topics.md` — fixed ENCOR→ENARSI, added memory update
  - `chapter-build.md` — added NOT-default warning, memory step
  - `generate-topology.md` — removed dead `labs/common/tools/export_diagrams.py` ref
  - `troubleshoot.md` — references `cisco-troubleshooting-1/references/` for detail
  - `inject-faults.md` — added memory update step

#### Skills (`/.agent/skills/`)

**`lab-workbook-creator/SKILL.md`**
- Added **ASCII Topology Diagram Standard** (Step 2):
  - Unicode box-drawing characters (`┌─┐│└┘┬┴`) mandatory — no `/`, `\`, plain `-`
  - Interface name **and** full IP/mask labeled on every link segment
  - Subnet label on horizontal bottom links
  - Chain topology example (linear) provided
  - Triangle topology example (hub + 2 branches) provided
- Added **Troubleshooting Ticket Format** (Section 9):
  - Headings describe **observable symptoms only** — never fault type or target device
  - Each ticket includes inline `inject_scenario_0N.py` command
  - Success criteria must be explicit
  - Diagnosis and fix in `<details>` spoiler blocks
  - ❌ Bad: `Ticket 1: AS Number Mismatch (Target: R2)`
  - ✅ Good: `Ticket 1 — R2 Reports No EIGRP Neighbors`
- Added **10-section workbook structure**:
  - Section 8: Solutions — lab objective configs only
  - Section 9: Troubleshooting Scenarios — workflow block + symptom-based tickets
  - Section 10: Lab Completion Checklist (Core Implementation + Troubleshooting)
  - Removed old "Automated Fault Injection (Optional)" section
- Added Common Issue: "Troubleshooting tickets in wrong section"

**Other Skills**
- `chapter-builder/SKILL.md` — updated non-default warning per workflow decision
- `chapter-topics-creator/SKILL.md` — added trigger phrases, fixed ENCOR→ENARSI
- `fault-injector/SKILL.md` — added trigger phrases, skill-level Common Issues
- `drawio/SKILL.md` — added trigger phrases, Common Issues section
- `gns3/SKILL.md` — full rewrite with platform selection guide, -#/--# headings, examples
- `cisco-troubleshooting-1/SKILL.md` — reduced from 824→130 lines, split into `references/`, deleted README.md

#### Documentation

**`CLAUDE.md`** (project root)
- Removed static "Lab Status" table
- Added Memory section with `@memory/` imports and Memory Convention
- Enforced one-lab-at-a-time workflow with explicit review gates

**Lab 01 Workbook**
- ASCII topology diagram updated to Unicode box-drawing standard (triangle topology)
- Troubleshooting tickets renamed with symptom-based headings
- Section 9 refactored with inject workflow block and per-ticket inject commands
- Section 10 checklist split into Core Implementation and Troubleshooting groups

### Deleted

- `.claude/commands/new-track.md` — conductor system removed
- **Old ENCOR content**:
  - `/conductor/` directory (tracks, archive, product.md, workflow.md)
  - `/docs/` (ENCOR-specific verification cheatsheets)
  - `gemini.md` (Gemini conductor reference)
  - `.prompts/` (old prompt templates)
  - All conductor-specific artifacts

- **Dead code references**:
  - `labs/common/tools/lab_utils.py` (removed from all skills)
  - `labs/common/tools/fault_utils.py` (removed)
  - `labs/common/tools/export_diagrams.py` (removed from commands)

---

## Git Commits

| Commit | Message |
|--------|---------|
| `adc1889` | feat: add memory system and rewrite stale slash commands |
| `7a82166` | feat(eigrp): generate baseline.yaml — 9-lab ENARSI chapter plan |
| `255a9e5` | feat(eigrp/lab-01): Classic Mode Adjacency — full DeepSeek Standard |
| `043a1a4` | style: standardise ASCII topology diagrams with box-drawing characters |
| `5a6d1ba` | fix(eigrp/lab-01): remove fault spoilers from headings and README |
| `f220cd2` | refactor: split Solutions and Troubleshooting into separate workbook sections |

---

## Key Design Decisions

See `memory/decisions.md` for full design decision log. Key decisions:

1. **One-Lab-at-a-Time Workflow** — Labs generated individually with review gates. Each lab's solutions chain to the next lab's initial-configs.

2. **Spec-Driven Architecture** — Two-layer spec: human `specs/[chapter]/chapter-spec.md` → machine `labs/[chapter]/baseline.yaml`.

3. **CCNP ENARSI 300-410** — Complete migration from ENCOR 350-401. All exam bullets, chapter names, and objectives updated.

4. **Symptom-Based Troubleshooting Tickets** — Scenario headings describe what students **observe**, not what broke. The fault is the answer (hidden in spoilers).

5. **GNS3 Apple Silicon (Dynamips only)** — c7200 and c3725 platforms. No VMware, VirtualBox, IOS-XR, or NX-OS.

---

## Summary

This session completed the foundational restructuring of the project from ENCOR→ENARSI with a production-grade workflow:

- ✅ Memory system established for cross-session continuity
- ✅ EIGRP chapter planned (9 labs) with comprehensive baseline.yaml
- ✅ Lab 01 generated to full DeepSeek Standard with 3 fault scenarios
- ✅ Workbook format standardized (10 sections, spoiler-free troubleshooting)
- ✅ ASCII topology diagram standard codified in skills
- ✅ All slash commands and skills updated for ENARSI context
- ✅ All dead ENCOR/conductor references removed

**Ready for**: Lab 01 review and approval → Lab 02 generation (Named Mode & Dual-Stack).

---

*Changelog generated 2026-02-23*
