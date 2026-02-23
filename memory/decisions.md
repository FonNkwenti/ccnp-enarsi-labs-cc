# Design Decisions

> Log significant architecture and workflow decisions with rationale.
> Append new entries at the top (newest first).

---

## 2026-02-23 Session — ENCOR→ENARSI Migration & Lab 01 Generation

**Summary:** Migrated project from CCNP ENCOR (350-401) to CCNP ENARSI (300-410). Established memory system, codified lab standards in skills, generated EIGRP baseline (9 labs) and Lab 01 full artifacts.

**Key Artifacts:**
- `memory/progress.md` + `memory/decisions.md` (memory system)
- `labs/eigrp/baseline.yaml` (9-lab chapter plan)
- `labs/eigrp/lab-01-classic-adjacency/` (full DeepSeek Standard: workbook + configs + topology + scripts + 3 fault scenarios)
- Updated 7 skills with standards + codified formats

**Key Commits:**
- `adc1889` — Memory system + slash commands
- `7a82166` — EIGRP baseline.yaml
- `255a9e5` — Lab 01 artifacts
- `043a1a4` — ASCII diagram standard (box-drawing)
- `5a6d1ba` — Spoiler-free troubleshooting
- `f220cd2` — Workbook refactor (10 sections)

**Decisions Made (see below for rationale):**
1. One-lab-at-a-time workflow (not batch)
2. Symptom-based troubleshooting tickets (headings don't reveal faults)
3. Separate workbook sections: Solutions (Sec 8) ≠ Troubleshooting (Sec 9)
4. Unicode box-drawing ASCII diagrams (not `/\`)
5. Ops-only README.md for fault injection (no challenge descriptions)

---

## 2026-02-23 — One-Lab-at-a-Time Workflow

**Decision:** Labs are generated one at a time with an explicit review gate between each lab.

**Rationale:** Each lab's `solutions/` becomes the next lab's `initial-configs/`. If a solution has errors, those errors chain forward into all subsequent labs. Reviewing before proceeding prevents compounding mistakes and allows refinements to topology, objectives, or config style.

**Rule:** The `chapter-build` skill (batch generation) exists but is NOT the default. Only use it when explicitly asked to batch generate and reviews will happen after.

---

## 2026-02-23 — Spec-Driven Workflow

**Decision:** Two-layer spec system: `specs/[chapter]/chapter-spec.md` (human intent) → `labs/[chapter]/baseline.yaml` (machine spec).

**Rationale:** The chapter-spec.md is written by the user before any generation starts. It captures exam bullets, desired labs, and topology intent in plain language. The `chapter-topics` skill converts it into a machine-readable `baseline.yaml` consumed by all generation skills. This keeps the human layer clean and the machine layer precise.

---

## 2026-02-23 — CCNP ENARSI 300-410 (not ENCOR 350-401)

**Decision:** This project targets CCNP ENARSI (300-410), not CCNP ENCOR (350-401).

**Rationale:** The project was cloned from an ENCOR project. All references to 350-401 exam objectives, ENCOR blueprint bullets, and ENCOR chapter names have been replaced with their 300-410 ENARSI equivalents.

**Chapters covered:** EIGRP, OSPF, BGP, Redistribution, VPN, Infrastructure Security, Infrastructure Services.

---

## 2026-02-23 — GNS3 Platform Constraint (Apple Silicon)

**Decision:** All labs use only `c7200` and `c3725` Dynamips images. No VMware, VirtualBox, IOS-XR, or NX-OS.

**Rationale:** The lab host runs Apple Silicon (M1/M2/M3). Only Dynamips is supported. See `.agent/skills/gns3/SKILL.md` for full platform selection guide.

---

## 2026-02-23 — Skills Submodule (`/.agent/skills`)

**Decision:** Lab generation skills live in `.agent/skills` as a git submodule.

**Rationale:** Skills can be updated independently with `git submodule update --remote .agent/skills`. Core skills: `lab-workbook-creator`, `fault-injector`, `chapter-topics-creator`, `chapter-builder`, `drawio`, `gns3`, `cisco-troubleshooting-1`.
