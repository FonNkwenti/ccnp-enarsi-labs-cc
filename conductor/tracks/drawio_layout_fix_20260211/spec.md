# Specification: Draw.io Layout Fix — Bypass Link Overlap

## Problem

When devices R1, R2, R3 are placed in a single vertical column (same X coordinate) and a bypass link exists between R1 and R3, the connection line visually crosses through R2. This is confusing for readers.

## Root Cause

The `generate_topo.py` script and SKILL.md style guide use fixed coordinates that place R1, R2, R3 at x=400 in a straight vertical chain. No layout rule addresses the case where a "skip" link bypasses intermediate devices.

## Solution

1. Add a **Layout Rule** to SKILL.md Section 4 that requires offsetting intermediate devices when bypass links exist, preventing visual overlap.
2. Update `generate_topo.py` to detect bypass links and shift intermediate devices horizontally to create a triangle/offset layout.

## Scope

- Update `.agent/skills/drawio/SKILL.md` — add Section 4.8 (Layout Rules).
- Update `.agent/skills/drawio/scripts/generate_topo.py` — dynamic coordinate adjustment.
- No existing diagram files are modified (user will fix manually).
