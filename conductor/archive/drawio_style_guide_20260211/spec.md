# Track Specification: Draw.io Visual Style Guide & Diagram Remediation

## Goal
Establish a canonical visual style guide for all Draw.io topology diagrams and update all existing diagrams and generation tooling to comply.

## Scope
- **Style Guide**: `.agent/skills/drawio/SKILL.md` Section 4
- **Generator Script**: `.agent/skills/drawio/scripts/generate_topo.py`
- **Dependent Skills**: `lab-workbook-creator`, `chapter-builder`, `chapter-topics-creator`
- **Existing Diagrams**: All `topology.drawio` files in `labs/eigrp/` and `labs/ospf/`

## Style Rules
1. **White connection lines** (`strokeColor=#FFFFFF`), never black.
2. **Device labels** positioned to the **left** of router icons.
3. **IP last octet labels** (`.1`, `.2`) near each router's interface endpoint.
4. **Title** at the top center of the canvas.
5. **Legend box** — black fill (`#000000`), white text (`#FFFFFF`), bottom-right.

## Deliverables
- Updated `drawio/SKILL.md` with comprehensive Visual Style Guide.
- Updated `generate_topo.py` producing compliant XML.
- Updated dependent skills referencing the style guide.
- All existing `topology.drawio` files updated to comply.

## Success Criteria
- Every `topology.drawio` in the repo matches the style guide.
- `generate_topo.py` produces compliant output.
- All skill files reference the style guide for diagram generation.
