# CCNP ENARSI (300-410) Lab Project

## Exam

- **Code**: 300-410 ENARSI
- **Name**: Implementing Cisco Enterprise Advanced Routing and Services
- **Platform**: GNS3 on Apple Silicon (Dynamips only — c3725, c7200)

## Spec-Driven Workflow

```
specs/[chapter]/chapter-spec.md   ← human intent (exam bullets, lab plan)
        ↓  chapter-topics skill
labs/[chapter]/baseline.yaml      ← machine-readable spec (consumed by skills)
        ↓  chapter-build or create-lab skill
labs/[chapter]/lab-NN-*/          ← DeepSeek Standard artifacts
        ↓  inject-faults skill (automatic)
labs/[chapter]/lab-NN-*/fault-injection/
```

### Before generating any labs

1. Read the chapter spec: `specs/[chapter]/chapter-spec.md`
2. Use `chapter-topics` skill to generate `labs/[chapter]/baseline.yaml`
3. Use `chapter-build` (multiple labs) or `create-lab` (single lab) skill
4. Fault injection runs automatically after lab creation

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
