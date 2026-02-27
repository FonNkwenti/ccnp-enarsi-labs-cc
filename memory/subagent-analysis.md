# Subagent Dispatch Analysis — lab-workbook-creator

> Created: 2026-02-26
> Decision: Dispatch Steps 3–7 (configs, diagram, scripts) as subagents instead of
> running them in main context. Preserves early-session context through all 10 labs.

---

## Before (Lab-04 measured, main-context lines)

| Category | Lines |
|---|---|
| workbook.md (10 sections) | ~650 |
| initial-configs/ (3 × R*.cfg) | ~210 |
| solutions/ (3 × R*.cfg) | ~270 |
| topology.drawio XML | ~180 |
| setup_lab.py | ~75 |
| drawio/SKILL.md read (§4.2–§4.7) | ~328 |
| fault-injector/SKILL.md read | ~142 |
| inject_scenario_01-03.py (3 scripts) | ~240 |
| apply_solution.py | ~80 |
| scripts/fault-injection/README.md | ~30 |
| **Total per lab** | **~2,205** |

Cumulative after 4 labs: ~8,820 lines consumed → early-session context (lessons.md,
baseline.yaml, chapter-spec) compressed out by lab 5–6.

---

## After (Lab-05 projected, main-context lines)

| Category | Where runs | Lines in main |
|---|---|---|
| workbook.md (10 sections) | main | ~650 |
| drawio/SKILL.md read | Subagent C | 0 |
| fault-injector/SKILL.md read | Subagent E | 0 |
| initial-configs/ | Subagent A | 0 |
| solutions/ | Subagent B | 0 |
| topology.drawio XML | Subagent C | 0 |
| setup_lab.py | Subagent D | 0 |
| inject scripts + apply + README | Subagent E | 0 |
| Subagent dispatch overhead (~5 prompts) | main | ~498 |
| **Total per lab (main context)** | | **~1,148** |

Lines offloaded to subagents per lab: ~3,213
**Main-context reduction: ~48%** (1,148 vs. 2,205)

---

## Offloaded to Subagents

| Subagent | Task | Forced reads it absorbs |
|---|---|---|
| A — Initial Configs | Write initial-configs/*.cfg | baseline.yaml (already read in Step 1) |
| B — Solution Configs | Write solutions/*.cfg | workbook.md Section 5/8 |
| C — Topology Diagram | Write topology.drawio | drawio/SKILL.md full read (328 lines) |
| D — Setup Script | Write setup_lab.py | assets/setup_lab_template.py |
| E — Fault Injection | Write scripts/fault-injection/ | fault-injector/SKILL.md full read (142 lines) |

The two biggest wins: drawio/SKILL.md (328 lines) and fault-injector/SKILL.md (142 lines)
never consume main-context space again.

---

## Long-Term Projection (Labs 6–10)

Without subagents, by lab 6 approximately 13,200 lines of prior lab content occupies
context, crowding out lessons.md, baseline.yaml, and chapter-spec.md. The known failure
modes from lessons.md (spurious network statements, empty fault scripts, wrong platform)
become likely again because the prevention rules are compressed out.

With subagents, main-context growth per lab is ~1,148 lines. After 10 labs: ~11,480 lines
of main-context total — comparable to the old 5-lab mark, meaning early-session context
(lessons.md: ~150 lines, baseline.yaml: ~120 lines) stays readable through all 10 labs.

---

## Dependency Graph

```
Step 1: Read inputs (main)
    ↓
Step 2: Write workbook.md (main)
    ↓
Step 3: Dispatch A+B+C+D in parallel (subagents)
    A: initial-configs/ ──┐
    B: solutions/      ──┤ all 4 must complete before Step 4
    C: topology.drawio ──┤
    D: setup_lab.py    ──┘
    ↓
Step 4: Dispatch E (sequential — needs solutions/ on disk)
    E: scripts/fault-injection/
```

solutions/ must exist on disk before Subagent E runs because E reads solution configs
to derive the inverse fault commands.

---

## Decision: Reverted to single-subagent (drawio only) — 2026-02-27

After lab-05 test, full 5-subagent approach was reverted. Measured costs:
- Lab-04 (no subagents): ~126,000 tokens estimated
- Lab-05 (5 subagents): ~184,000 tokens measured — ~46% more expensive

Root causes of overhead: subagents re-read files already in main context;
each carries its own system-prompt load; 5 API calls vs 1 counted against
Pro plan rate limits.

**Current approach:** Step 5 only — dispatch a single drawio subagent to
isolate the 328-line drawio/SKILL.md read. Everything else (configs, scripts,
setup_lab.py) runs in main context. Estimated saving vs. full subagent approach:
~50,000 tokens per lab. Fault-injector/SKILL.md read stays in main context
(142 lines — acceptable cost given it prevents the known empty-script defect).

## Risk: Submodule drift

`lab-workbook-creator/SKILL.md` lives in `.agent/skills` (git submodule).
Changes are local until committed to the submodule remote.
`git submodule update --remote .agent/skills` will overwrite local changes.
Commit to submodule remote after review.
