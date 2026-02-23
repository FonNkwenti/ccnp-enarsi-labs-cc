# Lab Progress

> This file is the source of truth for lab generation status.
> Update it after every lab session.

## Active Work

- **Chapter:** eigrp
- **Lab in progress:** —
- **Last completed lab:** lab-10-capstone-ii
- **Next action:** Review all EIGRP labs (01-10) — approve before proceeding to OSPF chapter
- **Quality repair completed:** 2026-02-23 — labs 03-10 repaired (48 fault scripts, 10 apply_solution.py, missing initial-configs, solutions, Section 9 workbook)
- **Platform finalized:** 2026-02-23 — all routers c7200 + IOS 15.3(3)XB12; named mode EIGRP throughout labs 02-10; spurious network statements fixed across all 54 configs

---

## EIGRP (300-410 Section 1.9, 1.1–1.5)

| Lab | Name | Status | Notes |
|-----|------|--------|-------|
| — | baseline.yaml | Approved | Generated 2026-02-23 — 10 labs (8 objective + 2 capstone), all c7200 + IOS 15.3(3)XB12, R1/R2/R3 core + R4 from lab-06 |
| 01 | Classic Adjacency | Review Needed | Foundation — 60 min, covers 1.9.b adjacency |
| 02 | Named Mode & Dual-Stack | Review Needed | Foundation — 75 min, covers 1.9.a-b dual-stack |
| 03 | Metrics & K-Values | Review Needed | Intermediate — 90 min, covers 1.9.f metrics |
| 04 | Feasible Successor | Review Needed | Intermediate — 90 min, covers 1.9.c-e loop-free path selection |
| 05 | Summarization | Review Needed | Intermediate — 75 min, covers 1.5 summarization |
| 06 | Stub Routing | Review Needed | Intermediate — 60 min, covers 1.9.d stubs, introduces R4 |
| 07 | Filtering & Route Maps | Review Needed | Advanced — 90 min, covers 1.2-1.3 filtering & route-maps |
| 08 | AD & Split Horizon | Review Needed | Advanced — 75 min, covers 1.1-1.3 AD & split horizon |
| 09 | Capstone I — Full Protocol Mastery | Review Needed | Advanced — 120 min, clean slate; all blueprint bullets; configuration challenge |
| 10 | Capstone II — Comprehensive Troubleshooting | Review Needed | Advanced — 120 min, clean slate; 5+ concurrent faults; troubleshooting challenge |

---

## OSPF (300-410 Section 1.10, 1.1–1.5)

| Lab | Name | Status | Notes |
|-----|------|--------|-------|
| — | baseline.yaml | Not generated | Run `chapter-topics` first |

---

## BGP (300-410 Section 1.11)

| Lab | Name | Status | Notes |
|-----|------|--------|-------|
| — | baseline.yaml | Not generated | Run `chapter-topics` first |

---

## Redistribution (300-410 Sections 1.4, 1.6–1.8)

| Lab | Name | Status | Notes |
|-----|------|--------|-------|
| — | baseline.yaml | Not generated | Run `chapter-topics` first |

---

## VPN (300-410 Sections 2.1–2.4)

| Lab | Name | Status | Notes |
|-----|------|--------|-------|
| — | baseline.yaml | Not generated | Run `chapter-topics` first |

---

## Infrastructure Security (300-410 Sections 3.1–3.4)

| Lab | Name | Status | Notes |
|-----|------|--------|-------|
| — | baseline.yaml | Not generated | Run `chapter-topics` first |

---

## Infrastructure Services (300-410 Sections 4.1–4.7)

| Lab | Name | Status | Notes |
|-----|------|--------|-------|
| — | baseline.yaml | Not generated | Run `chapter-topics` first |

---

## Status Key

| Symbol | Meaning |
|--------|---------|
| Not generated | No files created yet |
| In Progress | Currently being built |
| Review Needed | Generated — awaiting user approval |
| Approved | Reviewed and approved — ready to chain |
| Complete | Approved + fault-injection scripts done |
