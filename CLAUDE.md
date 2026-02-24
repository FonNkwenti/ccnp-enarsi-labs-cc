# CCNP ENARSI (300-410) Lab Project

## Exam

- **Code**: 300-410 ENARSI
- **Name**: Implementing Cisco Enterprise Advanced Routing and Services
- **Platform**: GNS3 on Apple Silicon (Dynamips only — c3725, c7200)

## Spec-Driven Workflow

Labs are built **one at a time** to allow review and refinement before chaining to the next lab. This is the default and only approved workflow.

```
specs/[chapter]/chapter-spec.md   ← exam bullets + optional preferences
        ↓  chapter-topics skill
labs/[chapter]/baseline.yaml      ← machine-readable spec (consumed by skills)
        ↓  skill backfills
specs/[chapter]/chapter-spec.md   ← now includes Generated Plan (topology, labs, coverage)
        ↓  create-lab skill (ONE lab at a time)
labs/[chapter]/lab-NN-*/          ← DeepSeek Standard artifacts
        ↓  inject-faults skill (automatic)
labs/[chapter]/lab-NN-*/fault-injection/
        ↓  REVIEW & APPROVE
        ↓  create-lab skill (next lab — chains from previous solutions/)
```

### Lab generation sequence

1. Read the chapter spec: `specs/[chapter]/chapter-spec.md`
2. Use `chapter-topics` skill → generates `labs/[chapter]/baseline.yaml`
3. Use `create-lab` skill for **one lab at a time**:
   - Lab 01: initial-configs generated from `baseline.yaml core_topology`
   - Lab N: initial-configs copied from Lab (N-1) `solutions/`
4. `inject-faults` skill runs automatically after each lab
5. **Review and approve the lab before proceeding to the next**
6. Repeat from step 3 for the next lab number

### Rules

- **Never generate more than one lab per session without explicit approval** to proceed
- **Never skip the review step** — each lab's solutions become the next lab's initial-configs
- The `chapter-build` skill (batch generation) is available but **not the default** — only use it when explicitly asked to generate multiple labs and reviews will happen afterwards

## Product Guidelines

### Voice & Tone
- **Scenario-based**: Frame every lab in a realistic enterprise narrative. Both framings are acceptable:
  - Third-person: "Acme Corp is deploying EIGRP across its WAN…"
  - First-person: "As a lead network engineer, your task is to…"
  Never present labs as abstract exercises.
- **Challenge-first**: Present topology and high-level objectives (Section 5) before solutions (Section 8). The student should attempt the challenge before seeing how.
- **Professional & authoritative**: Position workbooks as definitive ENARSI exam preparation material.

### Terminology
Use **Cisco official terminology** exclusively (exam-aligned):
- ✅ "Feasible Successor", "Administrative Distance", "Dead Interval", "Reported Distance", "Metric Weights"
- ❌ "backup route", "backup priority", "keepalive", "advertised distance"

### Workbook Design
- **10 required sections**: Concepts → Topology → Hardware → Base Config → Challenge → Verification → Cheatsheet → Solutions → Troubleshooting → Checklist
- **Solutions in `<details>` spoilers only** — never visible without a click
- **Troubleshooting tickets describe symptoms** — never reveal the fault in headings
- **ASCII diagrams use Unicode box-drawing** (`┌─┐│└┘┬┴`), not `/` or `\`
- **Every workbook includes a Cabling Table and Console Access Table**

### Python Style (Lab Scripts)
- Lightweight: clear variable names, brief inline comments where intent isn't obvious
- No formal docstrings or granular type annotations required — scripts are 50–80 line tools, not shared libraries
- **Critical — `\\n` escaping**: When generating Python via tool calls, always use `\\n` (double backslash) for newline literals inside strings. The JSON parser interprets `\n` as a literal newline, causing `SyntaxError`.

### Lab Progression
- Labs within a chapter are generated in **progressive difficulty**: Foundation → Intermediate → Advanced
- Each lab builds on the previous — Lab N's `initial-configs/` = Lab (N-1)'s `solutions/`
- **Add only, never remove** — no config commands are deleted between labs
- Optional devices enter at specific lab numbers (declared in `baseline.yaml available_from`)
- **Topology size**: minimum 3 devices, maximum 15 devices (core + optional combined)
- **Every chapter ends with Capstone I and Capstone II** (last 2 labs in every chapter):
  - **Capstone I** — full protocol configuration challenge (clean slate from IP addressing only; all blueprint bullets)
  - **Capstone II** — comprehensive troubleshooting challenge (clean slate; 5+ concurrent faults spanning all blueprint bullets)
  - Both capstones start from a clean slate — initial-configs are generated from `core_topology`, NOT from the previous lab's solutions

## Project Structure

```
specs/              # Exam blueprint + per-chapter specs
  exam-blueprint.md # Full 300-410 blueprint with topic mapping
  [chapter]/
    chapter-spec.md # Exam bullets, planned labs, topology notes

labs/               # Generated lab content (DeepSeek Standard)
  [chapter]/
    baseline.yaml   # Generated from spec — consumed by skills
    lab-NN-[name]/
      workbook.md
      topology.drawio
      initial-configs/
      solutions/
      setup_lab.py
      scripts/fault-injection/

memory/             # Cross-session continuity
tests/              # Artifact validation tests
.agent/skills/      # Lab generation skills (submodule)
```

## Chapter Map

| Folder | Blueprint Domain | Sections |
|---|---|---|
| `eigrp/` | Layer 3 Technologies | 1.9, 1.1–1.5 |
| `ospf/` | Layer 3 Technologies | 1.10, 1.1–1.5 |
| `bgp/` | Layer 3 Technologies | 1.11, 1.1–1.5 |
| `redistribution/` | Layer 3 Technologies | 1.4, 1.2, 1.3, 1.6–1.8 |
| `vpn/` | VPN Technologies | 2.1–2.4 |
| `infrastructure-security/` | Infrastructure Security | 3.1–3.4 |
| `infrastructure-services/` | Infrastructure Services | 4.1–4.7 |

## Memory

@memory/progress.md
@memory/decisions.md
@tasks/lessons.md

### Memory Convention

- `memory/progress.md` — lab generation status per chapter (update after every lab session)
- `memory/decisions.md` — append-only log of design decisions with rationale (newest first)
- After completing or approving a lab, update the status row in `memory/progress.md` before ending the session
