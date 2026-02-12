# Implementation Plan: Draw.io Visual Style Guide & Diagram Remediation

## Phase 1: Style Guide & Tooling
- [x] Task: Define Visual Style Guide in `.agent/skills/drawio/SKILL.md` Section 4.
- [x] Task: Update `generate_topo.py` to produce style-compliant XML (white links, left labels, IP octets, legend).
- [x] Task: Update `lab-workbook-creator` skill to reference style guide.
- [x] Task: Update `chapter-builder` skill to reference style guide and add validation checklist item.
- [x] Task: Update `chapter-topics-creator` skill to reference style guide.

## Phase 2: Existing Diagram Remediation
- [x] Task: Update all EIGRP `topology.drawio` files (labs 01-09) to comply with style guide.
- [x] Task: Update all OSPF `topology.drawio` files (labs 01-02) to comply with style guide. (Lab 03 already hand-styled by user.)
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Diagram Review' (visual review in Draw.io).
