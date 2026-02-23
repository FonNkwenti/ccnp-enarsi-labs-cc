# CCNP ENARSI (300-410) Lab Project

## Exam

- **Code**: 300-410 ENARSI
- **Name**: Implementing Cisco Enterprise Advanced Routing and Services
- **Platform**: GNS3 on Apple Silicon (Dynamips only — c3725, c7200)

## Spec-Driven Workflow

Labs are built **one at a time** to allow review and refinement before chaining to the next lab. This is the default and only approved workflow.

```
specs/[chapter]/chapter-spec.md   ← human intent (exam bullets, lab plan)
        ↓  chapter-topics skill
labs/[chapter]/baseline.yaml      ← machine-readable spec (consumed by skills)
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
      topology.png
      initial-configs/
      solutions/
      setup_lab.py
      fault-injection/

docs/               # Verification cheatsheets (per chapter)
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

## Lab Status

| Chapter | Labs | Status |
|---|---|---|
| EIGRP | — | Not started |
| OSPF | — | Not started |
| BGP | — | Not started |
| Redistribution | — | Not started |
| VPN | — | Not started |
| Infra Security | — | Not started |
| Infra Services | — | Not started |
