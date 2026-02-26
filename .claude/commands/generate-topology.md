Generate or update a Draw.io topology diagram for: $ARGUMENTS

## Pre-flight checks

1. Read `.agent/skills/drawio/SKILL.md` §4.2–§4.7 in full — all visual rules are defined there
2. Read the chapter's `baseline.yaml` — device list, links, IPs, and console ports for the active lab

## Workflow

Use the `drawio` skill. It defines all canvas rules, icon styles, label placement math, connection line colors, tunnel color codes, and arc waypoint formulas.

1. Read `baseline.yaml` for the devices and links active in this lab
2. Generate the `.drawio` XML starting from the §4.7 reference XML snippets — never write drawio XML from scratch
3. Run the post-write validation checklist from the skill before saving
4. Save to `labs/<chapter>/lab-NN-<slug>/topology.drawio`

## Arguments format

Provide the lab path: `labs/<chapter>/lab-NN-<slug>`

## After generation

No memory update required — topology is reviewed as part of lab artifact approval.
