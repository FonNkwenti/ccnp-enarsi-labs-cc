# Lessons Learned — CCNP Lab Development

Patterns, bugs, design decisions, and guidance from CCNP ENCOR lab development. Reference this when starting a new certification or extending skills.

---

## Part 1: Patterns (What Worked Well)

### DeepSeek Standard Lab Package

**Pattern:** Each lab includes workbook + configs + topology + scripts + fault injection.

**Why:** Comprehensive, self-contained artifact. Students can work offline. Instructor can script setup/reset.

**Apply to:** Every new certification. Do not skip components.

```
lab-NN-[slug]/
├── workbook.md               # 10 sections, all required
├── initial-configs/          # per-device base state
├── solutions/                # per-device solution
├── topology.drawio           # editable diagram
├── setup_lab.py              # Netmiko automation
└── scripts/fault-injection/  # 3+ scenarios, apply_solution.py, README.md
```

---

### Triangle Topology (Hub + 2 Branches)

**Pattern:** 3-router topology with R1 (hub) connected to R2 and R3, plus R2-R3 cross-link.

**Why:**
- Large enough for multiple paths (successor + feasible successor scenarios)
- Small enough for manual troubleshooting
- Mirrors real enterprise (headquarters + 2 sites)
- Natural progression: R1-R2-R3 adjacencies, then R2-R3 alternate path
- Scales: add R4 (stub) for advanced labs, add R5/R6 for full mesh

**Example topologies by protocol:**
- **EIGRP/OSPF**: Hub + 2 branches (triangle) — demonstrates path selection, metric tuning
- **BGP**: Linear chain (HQ → Region → Branch) — demonstrates AS relationships, path propagation
- **Redistribution**: Two separate triangles merged (EIGRP zone + OSPF zone) — demonstrates boundary

---

### Loopback0 as Management Interface

**Pattern:** Every router has Loopback0 with IP from a /32 reserved subnet (e.g., `10.0.0.x/32`).

**Why:**
- Never goes down (doesn't depend on physical interfaces)
- Stable management target for SSH, Syslog, NTP, SNMP
- Routing protocol advertises it by default
- Mirrors real enterprise (management addresses on loopbacks)

**Convention:**
- `10.0.0.1/32` for R1, `10.0.0.2/32` for R2, etc.
- Optional: `2001:db8::x/128` for IPv6 when needed
- Loopbacks are **always** EIGRP/OSPF passive interfaces (never send Hellos)

---

### Console Port Convention

**Pattern:** R1=5001, R2=5002, RN=500N.

**Why:** Trivial to remember, deterministic, no lookup table needed.

**Critical:** Hardcode this in baseline.yaml and all scripts. Never deviate.

---

### Progressive Difficulty Levels

**Pattern:** Foundation → Intermediate → Advanced progression across labs.

**Foundation (Labs 01–03)**
- Core technology concepts
- Single protocol in "default" mode
- Success = basic reachability

**Intermediate (Labs 04–06)**
- Advanced features of the protocol
- Multi-parameter tuning
- Multi-protocol interaction starts

**Advanced (Labs 07–09)**
- Real-world complexity (filtering, redistribution, security)
- Troubleshooting integration
- Multiple technologies interacting

**Why:** Cognitive load management. Students build mental models progressively.

---

### Symptom-Based Troubleshooting Tickets

**Pattern:** Tickets describe the **symptom** ("R2 has no EIGRP neighbors"), not the fault ("AS mismatch on R2").

**Why:**
- Students practice diagnosis (the actual job)
- Prevents spoilers in the heading
- Diagnosis is the learning objective, not the fault identification

**Anatomy of a good ticket:**
```
### Ticket N — [Observable Symptom Description]

[1-2 sentence business context — what the student was told]

**Inject:** `python3 scripts/fault-injection/inject_scenario_0N.py`

**Success criteria:** [Specific, testable outcome]

<details>
<summary>Click to view Diagnosis Steps</summary>
[show commands and interpretation]
</details>

<details>
<summary>Click to view Fix</summary>
[commands to resolve + verification]
</details>
```

---

### Pre-Reserved IPv4 + IPv6 Addressing

**Pattern:** In `baseline.yaml`, reserve ALL IP ranges for all devices before Lab 01 exists.

**Why:**
- Lab N uses only the IPs from baseline — no surprises
- IPv6 addition in Lab 02 uses pre-reserved addresses
- Prevents "oops, we need to renumber everything" later
- Device lifecycle is clear (R4 enters at Lab 06 with reserved 10.0.0.4 + 2001:db8::4)

**Example:**
```yaml
core_topology:
  devices:
    - name: R1
      loopback0:
        ipv4: 10.0.0.1/32      ← reserved now, used in Lab 01
        ipv6: 2001:db8::1/128  ← reserved now, used in Lab 02

optional_devices:
  - name: R4
    loopback0:
      ipv4: 10.0.0.4/32        ← reserved now, activated Lab 06
      ipv6: 2001:db8::4/128
    available_from: 6
```

---

## Part 2: Bugs & Pitfalls

### ASCII Diagram with `/` and `\` Characters

**Pitfall:** Early EIGRP diagrams used `/` and `\` to draw links.

**Problem:**
- Hard to align in monospace
- Looks unprofessional
- Ambiguous what connects to what
- Maintenance nightmare (add a device = re-draw everything)

**Fix:** Use Unicode box-drawing characters (`┌─┐│└─┘┬┴`).

**Lesson:** Invest in diagram standard early. Box-drawing looks polished and is maintainable.

---

### Spoiler Headings in Troubleshooting

**Pitfall:** Original ENCOR labs had headings like "Scenario 1: AS Number Mismatch (Target: R2)".

**Problem:**
- Headings reveal the fault
- Students read the heading, already know the answer
- Defeats the purpose of troubleshooting practice

**Fix:** Use symptom-based headings ("R2 Reports No EIGRP Neighbors") with fault details in `<details>` blocks.

**Lesson:** Spoiler-free sections require separate design. Don't mix Solutions and Troubleshooting in the same workbook section.

---

### Troubleshooting Content Duplication

**Pitfall:** ENCOR labs had full ticket descriptions in both `workbook.md` (Section 8) AND `scripts/fault-injection/README.md`.

**Problem:**
- Maintenance burden (update one, forget the other)
- Students confused by conflicting descriptions
- README became 1000+ lines when it should be ops-only

**Fix:**
- `workbook.md` Section 9: Troubleshooting Scenarios (tickets with diagnosis/fix in spoilers)
- `scripts/fault-injection/README.md`: ops-only (run this script, restore with this command)
- README references workbook: "See workbook.md Section 9 for the challenge"

**Lesson:** Separate concerns. Workbook = challenge + pedagogy. README = operations + scripts.

---

### No Memory System Across Sessions

**Pitfall:** ENCOR was Gemini conductor-based. No persistent state tracking between Claude sessions.

**Problem:**
- Forgot which labs were done, which were in progress
- Couldn't resume a partially completed workbook
- Team didn't know current status

**Fix:** Memory system (2026-02-23 session):
- `memory/progress.md` — per-chapter status table
- `memory/decisions.md` — design decisions log
- Both auto-loaded via `@` imports in CLAUDE.md

**Lesson:** Build memory system on day 1, not day 100. Use Claude's built-in import system.

---

### Standards Not Encoded in Skills

**Pitfall:** ENCOR skills had ad-hoc formats. Each lab looked slightly different.

**Problem:**
- Inconsistent workbook structure
- Different troubleshooting formats
- ASCII diagrams styled differently
- Hard to maintain, hard to extend

**Fix:** Codify everything in skill SKILL.md:
- 10-section workbook template
- Troubleshooting ticket format (symptom headings, spoiler blocks)
- ASCII diagram standard (box-drawing, labeled links)
- Console port convention
- Device naming conventions

**Lesson:** Skills are living documentation. Encode all patterns and standards there. Future labs inherit the standard.

---

### Config Chaining Breaks Silently

**Pitfall:** Lab N's initial-configs accidentally removed a command that Lab N-1 had.

**Problem:**
- Adjacency broke in Lab 4 because Lab 3 solution was missing a network statement
- Student blamed the lab, not realizing the configs were corrupted
- Hard to trace (had to manually diff all solutions)

**Fix:**
- **Strict rule**: Lab N initial-configs = EXACT copy of Lab N-1 solutions
- **No editing** of initial-configs between labs
- **Add only** rule: Lab N solution ⊃ Lab N-1 solution (subset or equal, never less)
- **CI check** (future): validate chaining with automated diff

**Lesson:** Chaining is fragile. Make it a hard rule, verify it programmatically.

---

### Auto-Summary Enabled in Classic EIGRP

**Pitfall:** Classic EIGRP has `auto-summary` **enabled by default**.

**Problem:**
- Student forgets `no auto-summary`
- Discontiguous networks (e.g., 172.16.x networks) summarize to classful boundaries
- Routes disappear from tables (summarized to null0)
- Confusing error: route exists but is unreachable

**Fix:**
- Always include `no auto-summary` in solution configs
- Explicitly teach why (discontiguous network scenario)
- Mention in workbook Section 1 (Concepts)

**Lesson:** Defaults are silent killers. Always teach the "why" behind defensive config choices.

---

### Passive Interface on All Loopbacks (Best Practice)

**Pattern:** All loopback interfaces should be EIGRP/OSPF passive.

**Why:**
- Loopbacks are management interfaces, not transit links
- Passive prevents unnecessary multicast traffic
- Mirrors real enterprise best practice

**Config:**
```
router eigrp 100
 passive-interface Loopback0
```

**Why it's easy to forget:** Not obvious that Loopbacks are included in network statements, so students don't think to make them passive.

**Lesson:** Encode this as a requirement in Section 5 (Lab Challenge). "Configure Lo0 as passive on all routers."

---

### Netmiko Telnet Timeout Issues

**Pitfall:** `setup_lab.py` scripts occasionally timeout on slow GNS3 instances.

**Problem:**
- Telnet connection succeeds but enable prompt doesn't respond in time
- Script appears to hang
- User has to Ctrl+C and re-run

**Fix:**
```python
device = {
    "device_type": "cisco_ios_telnet",
    "timeout": 15,                 # was 10, increased
    "global_delay_factor": 2,      # added, slows down Netmiko
}
```

**Lesson:** GNS3 on resource-constrained hardware needs generous timeouts. Document in `setup_lab.py` comments.

---

### show ip eigrp topology — Critical for Understanding

**Pitfall:** Students troubleshooting adjacency issues but didn't use `show ip eigrp topology`.

**Problem:**
- They only looked at `show ip eigrp neighbors` (shows current neighbors)
- Didn't see the full picture: FD, RD, successors, feasible successors
- Misdiagnosed "no routes" as "no neighbors"

**Fix:**
- Make `show ip eigrp topology` mandatory in Section 7 (Verification Cheatsheet)
- Explain FD, RD, FC in Section 1 (Concepts)
- Verification & Analysis section shows sample output with annotations

**Lesson:** Teach the full diagnostic arsenal, not just the obvious commands.

---

### Split Horizon in Hub-Spoke Topology

**Pitfall:** R1 (hub) sends a route back out the interface it arrived on? No — split horizon prevents it.

**Problem:**
- Students expect R1 to advertise R3's loopback to R2 via the R1-R2 link
- It doesn't, because split horizon is enabled by default
- Seems like a bug ("why can't R2 reach R3?")
- Actually it's a feature (prevents loops)

**Fix:**
- Explain split horizon in Section 1 (Concepts) before the lab even starts
- Make a ticket specifically about split horizon behavior (Lab 08)
- Show in Verification & Analysis: `show ip eigrp interfaces detail` (confirms split horizon on each interface)

**Lesson:** Non-obvious defaults (split horizon, passive interfaces, auto-summary) need explicit teaching, not just "it's configured this way."

---

## Part 3: Design Decisions & Rationale

### Why baseline.yaml Instead of Starting Fresh

**Decision:** Two-layer spec: human `specs/[chapter]/chapter-spec.md` → machine `labs/[chapter]/baseline.yaml`.

**Rationale:**
1. **Device lifecycle management** — R4 (stub) enters at Lab 06, stays through 09. You need a single source of truth for all devices, not scattered definitions.
2. **Config chaining** — Lab N's initial-configs must equal Lab N-1's solutions. Baseline.yaml makes this explicit.
3. **Reproducibility** — If you regenerate Lab 05, it uses the exact same IPs, device roles, console ports. No surprises.
4. **Programmability** — Skills can parse baseline.yaml, generate initial-configs, validate assumptions.

**Alternative considered:** Each lab defines its own devices/IPs (easier initially, much harder at scale).

---

### Why 3 Routers Minimum for Foundation Labs

**Decision:** Foundation labs (Labs 01–03) use R1, R2, R3 (minimum viable setup).

**Rationale:**
1. **2 routers too small** — Shows only basic adjacency, no path selection, no multi-hop routing. Not enough to learn EIGRP concepts.
2. **4+ routers too complex** — Too many links to draw, too many adjacencies to verify. Students lose the forest for the trees.
3. **3 routers sweet spot** — Hub + 2 spokes shows:
   - Direct adjacency (R1-R2, R1-R3)
   - Indirect path (R2-R3 via R1)
   - Multi-hop distance calculations (FD, RD)
   - Path selection scenarios (successor vs. feasible successor)

**Scaling:** Optional devices (R4+) activate in later labs for advanced scenarios.

---

### Why c7200 for Hub, c3725 for Branches

**Decision:** Platform selection: Hub (R1) = c7200, Branches (R2, R3) = c3725.

**Rationale:**
1. **c7200 specs** (512MB RAM, multiple slots):
   - More interfaces (hub connects to many branches)
   - More features (crypto, advanced modules)
   - Mirrors real enterprise (hub has more capability)

2. **c3725 specs** (256MB RAM, 2 slots):
   - Simpler platform (2 FE + 1 serial)
   - Lower resource usage (GNS3 on laptop won't choke)
   - Enough for branch router (needs 2–3 interfaces typically)

3. **Mirrors real architecture** — Enterprises run higher-end gear at hub, commodity gear at branches.

**Alternative considered:** All routers same platform (simpler, but unrealistic and wastes resources).

---

### Why Fault Injection Scripts

**Decision:** Automated Python scripts (Netmiko) to inject faults, not manual "configure R2 wrong and send to student."

**Rationale:**
1. **Reproducibility** — Run the same fault 10 times, get identical state each time.
2. **Self-study** — Student can troubleshoot offline without instructor setting up faults.
3. **Speed** — Inject a fault in 2 seconds, not 2 minutes of manual config.
4. **Safety** — Script won't accidentally misconfigure; human might.
5. **Automation** — Lab instructor can rotate through students, injecting different faults.

**Alternative considered:** Written instructions ("On R2, type: `no router eigrp 100`..."). Too error-prone, too slow.

---

### Why `<details>` Spoilers in Workbook

**Decision:** Solution configs and diagnosis steps wrapped in HTML `<details>` collapsible blocks.

**Rationale:**
1. **Progressive disclosure** — Student sees the challenge first, tempted by "Click to view" but doesn't automatically see the answer.
2. **Honors the attempt** — Forces a moment of decision: "Do I really need to look?" Nudges toward trying first.
3. **Printable** — If printed, spoilers are collapsed (answer not on page 1).
4. **Search-friendly** — Content is still in the HTML, searchable, but not immediately visible.

**Alternative considered:** Separate solution PDF. Too clunky, easy to lose, doesn't encourage the "try first" mindset.

---

### Why Separate Troubleshooting Section

**Decision:** Troubleshooting Scenarios (Section 9) ≠ Solutions (Section 8).

**Rationale:**
1. **Cognitive load** — Lab Implementation and Troubleshooting are different activities:
   - Implementation: "Follow steps 1–5, verify at each step." (Guided learning)
   - Troubleshooting: "Figure it out from symptoms." (Open-ended practice)
2. **Pedagogical purpose differs** — Implementation builds muscle memory. Troubleshooting builds diagnosis skills.
3. **Easier to navigate** — Student completing implementation jumps to Section 10 (checklist). Student practicing troubleshooting goes to Section 9.

**Alternative considered:** Mix them in one "Solutions" section. Confusing, hard to distinguish intent.

---

### Why no auto-summary

**Decision:** Classic EIGRP labs include `no auto-summary` explicitly.

**Rationale:**
1. **Default is wrong** — auto-summary enabled by default; modern networks are discontiguous. Students will get burned if we don't teach the why.
2. **Educational value** — Teaches "verify defaults, don't assume."
3. **Real-world alignment** — Every enterprise network disables auto-summary.

**Alternative considered:** Leave auto-summary enabled, explain why later. Too confusing; students blame the lab instead of understanding the default.

---

## Part 4: Guidance for New Certifications

### Day 1: Set Up Memory System

Before writing any lab content:
```
memory/
├── progress.md       # per-chapter status table
├── decisions.md      # design decisions log
└── (config in CLAUDE.md with @ imports)
```

**Why:** You'll forget what state you're in. Memory system is the undo button.

---

### Day 2: Codify Standards in Skills

Before generating Lab 01:
- Define workbook sections (use 10 as template)
- Define topology shapes (chain? triangle? full mesh?)
- Define troubleshooting ticket format
- Define ASCII diagram standard
- Define device naming, console port convention

**Why:** Consistency scales. One skill update fixes all future labs.

---

### Day 3: Pick Topology Shapes That Recur

Identify the 2–3 topology patterns you'll use across the chapter:
- **Chain (linear)**: HQ → Region → Branch (for path propagation)
- **Triangle (hub + 2 spokes)**: Hub-and-spoke with one cross-link (for path selection)
- **Full mesh**: All devices connected to all others (for redistribution scenarios)
- **Partial mesh**: Hub + 4 spokes (for advanced protocols)

**Why:** Reduces design work. You're reusing the same structure, just changing configs.

---

### Day 4: Reserve All IP Addresses in baseline.yaml

Before Lab 01 is written, populate baseline.yaml with:
- All core device IPs (IPv4 + IPv6)
- All optional device IPs (with `available_from` field)
- All link subnets
- All loopback ranges

**Why:** Labs lock to this. No surprises mid-chapter.

---

### Use Exam Blueprint as Chapter Structure

Map exam domains → chapters (1:1):
- CCNP ENARSI 300-410:
  - Domain 1 (Layer 3) → 4 chapters (EIGRP, OSPF, BGP, Redistribution)
  - Domain 2 (VPN) → 1 chapter (VPN)
  - Domain 3 (Security) → 1 chapter (Infrastructure Security)
  - Domain 4 (Services) → 1 chapter (Infrastructure Services)

**Why:** Guaranteed exam coverage. No blind spots.

---

### Build Lab 01 to Full DeepSeek Standard First

Fully complete the first lab (all 10 workbook sections + all scripts + all fault scenarios) before generating Lab 02.

**Why:**
- Catches structural issues early (while you can still change the template)
- Tests the skill on realistic content
- Gives you a reference for the next 8 labs

---

## Part 5: For Skill Extensions

### Always Add Trigger Phrases

In SKILL.md frontmatter `description` field:
```yaml
description: "Creates a lab when user says 'generate lab N', 'create a lab',
'build [protocol] lab', 'write a workbook'. Use when chapter-builder invokes it..."
```

**Why:** Users type different things. Triggers let Claude understand intent without the user knowing the exact skill name.

**Rule:** Max 1024 chars. No XML angle brackets.

---

### Use -# and --# Heading Structure

```markdown
# Skill Name              ← top-level, not in SKILL.md body
-# Instructions          ← main section (use -# not ##)
--# Step 1: Something    ← substep (use --# not ###)
---                      ← separator (visual break)
-# Common Issues         ← main section
```

**Why:** Anthropic guide standard. Easier for Claude to parse. Looks cleaner.

---

### Add Common Issues Section

Every skill needs at least 3 Common Issues with Cause + Solution:

```markdown
-# Common Issues

--# Problem: [What goes wrong]
- **Cause:** [Why it happens]
- **Solution:** [How to fix it]
```

**Why:** Skills are tools. Users need debugging guidance.

---

### Level 3 Resources for External Files

If your skill references templates, scripts, or reference docs:
```
.agent/skills/my-skill/
├── SKILL.md                 ← main guide (under 5,000 words)
└── references/
    ├── template_01.py       ← Level 3: loaded on demand
    ├── methodologies.md
    └── examples.md
```

**Why:** Keeps SKILL.md lean. Complex details don't clutter the main narrative.

---

### No README.md Inside Skill Folders

Violates Anthropic guide. Put content in SKILL.md and references/ instead.

**Why:** README.md makes the skill harder to parse. Skills should be self-contained in SKILL.md.

---

### Keep SKILL.md Under 5,000 Words

If you exceed 5,000 words:
1. Move detailed examples to `references/examples.md`
2. Move methodologies to `references/methodologies.md`
3. Link from SKILL.md: "See `references/methodologies.md` for full list"

**Why:** Claude reads faster, context window is used efficiently, skill is easier to maintain.

---

### Provide Worked Examples

End every skill with an "Examples" section showing realistic scenarios:

```markdown
-# Examples

User: "Generate OSPF Lab 05 for the ENARSI series."

Actions:
1. Read `labs/ospf/baseline.yaml`
2. Copy Lab 04 solutions as Lab 05 initial-configs
3. Generate workbook with Section 5 objectives focusing on:
   - Multi-area OSPF design
   - ABR/ASBR roles
4. Include 3 troubleshooting scenarios around area misconfiguration
```

**Why:** Grounds the skill in reality. Users see exactly how to invoke it.

---

## Appendix: Checklist for New Certification

Use this checklist when starting a new exam certification (not just new chapters):

- [ ] Memory system created (`memory/progress.md`, `memory/decisions.md`)
- [ ] Spec-driven structure in place (`specs/[chapter]/chapter-spec.md` → `labs/[chapter]/baseline.yaml`)
- [ ] Exam blueprint fully mapped (check 300-410, 350-401, etc. official docs)
- [ ] Lab progression designed (Foundation → Intermediate → Advanced)
- [ ] Topology shapes identified (2–3 patterns that recur)
- [ ] Device naming convention locked in (R1–R15, minimum 3, maximum 15 per chapter)
- [ ] Console port convention locked in (5001–500N, where N matches router number)
- [ ] IPv4 + IPv6 addressing pre-reserved in baseline.yaml
- [ ] Workbook structure documented in skill (10 sections)
- [ ] ASCII diagram standard codified (box-drawing, labeled links)
- [ ] Troubleshooting ticket format defined (symptom headings, spoiler blocks)
- [ ] DeepSeek Standard artifacts identified (workbook, configs, topology, scripts, fault injection)
- [ ] Lab 01 fully generated and reviewed
- [ ] LESSONS_LEARNED.md (this file) referenced

---

*Last Updated: 2026-02-23*
*Drawn from CCNP ENCOR (350-401) and CCNP ENARSI (300-410) lab development.*
