Generate all labs for a chapter with proper chaining and continuity: $ARGUMENTS

> **NOT the default workflow.** Use `/create-lab` for normal lab generation (one lab at a time with reviews).
> Only use this command when explicitly asked to batch generate a chapter and reviews will happen after all labs are complete.

## Pre-flight checks

1. Read `labs/<chapter>/baseline.yaml` — must exist before running this command
2. Read `memory/progress.md` — confirm no labs for this chapter are already in progress

## Workflow

Use the `chapter-builder` skill. It will:

1. Generate Lab 01 from `baseline.yaml core_topology` (IP only, no protocol config in initial-configs)
2. For each subsequent lab: copy Lab (N-1) `solutions/` as initial-configs, then generate
3. Run `fault-injector` skill after each lab
4. Apply drawio Visual Style Guide to each `topology.drawio`

## Chaining rules

| Lab | initial-configs source | New devices |
|-----|------------------------|-------------|
| 01 | baseline core_topology (IP only) | Core devices |
| 02 | Lab 01 solutions/ | None (unless declared) |
| 03 | Lab 02 solutions/ | + devices with available_from: 3 |
| N  | Lab (N-1) solutions/ | As declared in baseline.yaml |

## Post-generation validation checklist

- [ ] All devices use IPs from baseline.yaml
- [ ] Lab N initial-configs match Lab (N-1) solutions exactly
- [ ] New devices are only added when declared in baseline.yaml
- [ ] No configs are removed between labs
- [ ] Each topology.drawio shows correct devices per lab
- [ ] Each topology.drawio follows the drawio Visual Style Guide

## Arguments format

- `eigrp` — generate all labs defined in baseline.yaml
- `ospf 5-8` — generate only labs 5 through 8

## After generation

Update `memory/progress.md`:
- Set all generated labs to **Review Needed**
- Set "Active Work → Next action" to: "Review all <chapter> labs before approving"
