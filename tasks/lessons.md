# Lessons Learned

> Append-only. New entries at the top (newest first).
> Each lesson: what triggered it → the failure pattern → the prevention rule.
> This file is distinct from `memory/decisions.md` (which logs design choices).
> **Read this file at the start of every lab generation session.**

---

## 2026-02-24-L6 — topology.drawio generated as plain rectangles, ignoring the drawio skill entirely

**Trigger:** Lab 01 `topology.drawio` was written from scratch as colored rounded rectangles
with embedded labels and default-black connection lines. The drawio skill was never read.
Every visual rule was violated: no Cisco icons, no white lines, no separate label cells,
no last-octet labels, no black legend box, wrong title size, no PNG export.

**Failure pattern:** `lab-workbook-creator/SKILL.md` Step 5 said "invoke the drawio skill"
but this was a soft suggestion — no hard stop required reading `drawio/SKILL.md` before
writing XML. Without the reference snippets in working memory, ad-hoc XML was written
that satisfied none of the visual style requirements.

**Prevention rule:**
- Before writing any `topology.drawio` XML, read `drawio/SKILL.md` §4.2–§4.7 in full
- Always start from the §4.7 reference XML snippets — never write drawio XML from scratch
- Run both the pre-write and post-write checklists in `lab-workbook-creator/SKILL.md` Step 5
- A topology is not complete until every checklist item passes
- The `.drawio` file is the only required diagram artifact — no PNG export

---

## 2026-02-23-L5 — Platform/IOS version must be confirmed before generating any configs

**Trigger:** Named mode EIGRP configs (labs 02-10) were generated for `c3725` running IOS 12.4.
Named mode requires IOS 15.0+. The result was a wasted full revert cycle:
commit `4e19874` (convert 70+ configs to classic mode) → commit `1dab4e2` (revert) →
commit `5e33c9d` (fix: switch all to c7200 + IOS 15.3(3)XB12).

**Failure pattern:** The generation skill assumed the platform from context without reading
`baseline.yaml` to confirm the IOS image and checking whether the config syntax it was
about to produce is supported on that image.

**Prevention rule:**
- Before generating any router config, read `baseline.yaml` → `core_topology.devices[*].ios_image`
- If the lab uses named mode EIGRP, OSPF process variants, or any IOS 15+ feature,
  verify the image version is ≥ 15.0 before writing a single config line
- If image version and config syntax are inconsistent, STOP and surface the conflict — do not
  silently fall back to a different syntax and generate 70 configs that need to be reverted

---

## 2026-02-23-L4 — Spurious network statements propagate silently through all chained labs

**Trigger:** Every router in labs 02-10 (54 configs) contained network statements for
links that did not exist on that router:
- R1 had `network 10.23.0.0 0.0.0.3` (R2-R3 link — no R1 interface)
- R2 had `network 10.13.0.0 0.0.0.3` (R1-R3 link — no R2 interface)
- R3 had `network 10.12.0.0 0.0.0.3` (R1-R2 link — no R3 interface)

These propagated invisibly because each lab's initial-configs are copied from the previous
lab's solutions/, so the error multiplied across 9 labs × 6 configs = 54 files.

**Failure pattern:** The skill generated network statements by iterating all topology subnets
rather than only the subnets reachable via that router's own interfaces. No cross-check
between "interfaces this router has" and "network statements being written" was performed.

**Prevention rule:**
- When writing any `network` statement under `router eigrp` or `router ospf`, verify:
  the subnet matches an interface that exists on THIS router in the topology
- The check is: `interface IP + wildcard` must fall within one of the router's own interface
  addresses as declared in `baseline.yaml core_topology`
- After generating initial-configs for lab-01 (or any lab that starts a new chain),
  manually trace each network statement to a specific interface before proceeding

---

## 2026-02-23-L3 — Optional device introduction breaks chaining if solutions/ are incomplete

**Trigger:** R4 enters in lab-06. Labs 06, 07, and 08 were all missing:
- `initial-configs/R4.cfg` (should be lab-05 solutions/R4 — but R4 doesn't exist in lab-05,
  so it must be generated from `baseline.yaml available_from`)
- `solutions/R4.cfg` in labs 06, 07, 08 (R4 config that chains forward)
- Updated `solutions/R1-R3.cfg` to include the new link to R4

**Failure pattern:** The skill generated the workbook and fault scripts for labs 06-08 but
skipped the config work for the new device. The chaining assumption ("copy previous solutions")
doesn't cover the case where a new device appears mid-chapter.

**Prevention rule:**
- When a lab's `baseline.yaml available_from` field introduces a new device,
  that lab's generation must explicitly:
  1. Create `initial-configs/[new_device].cfg` from `baseline.yaml core_topology`
     (not from previous solutions — the device has no prior history)
  2. Add the link between existing devices and the new device to ALL existing
     devices' `solutions/` configs in that lab
  3. Carry `solutions/[new_device].cfg` forward into the next lab's `initial-configs/`
- After generating a lab that introduces a new device, verify: `solutions/` contains
  one `.cfg` per active device (existing + newly introduced)

---

## 2026-02-23-L2 — `apply_solution.py` is silently omitted when fault scripts are generated

**Trigger:** Labs 03-10 all had `inject_scenario_NN.py` files but were missing
`apply_solution.py`. The fault-injection skill generated inject scripts without
generating the corresponding remediation script.

**Failure pattern:** `apply_solution.py` is a required DeepSeek Standard artifact but is
easily skipped because it isn't created by the same loop that creates inject scripts.
There is no generation-time check that flags its absence.

**Prevention rule:**
- After any fault-injection run, verify the following files exist in
  `scripts/fault-injection/`:
  - `apply_solution.py` — exactly one, always present
  - `inject_scenario_NN.py` — one per troubleshooting ticket in workbook Section 9
  - `README.md` — exactly one, always present
- The count of `inject_scenario_*.py` must equal the count of fault tickets in Section 9
- If `apply_solution.py` is missing: do not mark the lab complete — generate it immediately

---

## 2026-02-23-L1 — Empty script stubs are worse than no scripts

**Trigger:** Labs 03-09 were initially generated with `inject_scenario_NN.py` files that
contained empty function bodies or `pass` statements — syntactically valid Python but
functionally useless. The artifact appeared to exist (Glob found it) but would silently
do nothing when run.

**Failure pattern:** The generation skill created file skeletons to satisfy the artifact
checklist without completing the implementation. The review gate didn't catch it because
file existence was confirmed but content wasn't inspected.

**Prevention rule:**
- A fault script is only complete when it contains real Netmiko `cisco_ios_telnet`
  connection logic: device dict, `ConnectHandler`, and a `send_config_set()` call
  with the actual fault commands
- After generating fault scripts, spot-check at least one `inject_scenario_NN.py`
  per lab by reading its content — verify it contains `ConnectHandler` and a
  non-empty command list
- Scripts with `pass`, `# TODO`, or empty command lists (`[]`) are defects, not drafts
