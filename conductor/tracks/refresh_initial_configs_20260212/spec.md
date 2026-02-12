# Track Spec: refresh_lab.py — Load Initial Configs Instead of Solutions

## Problem Statement

All 9 EIGRP `refresh_lab.py` scripts load router configs from `solutions/` instead of
`initial-configs/`. The purpose of `refresh_lab.py` is to reset routers to the lab's
**starting state** so the student can begin (or restart) the exercises. Loading solutions
defeats the purpose — the student would see the completed config instead of the blank slate.

## Scope

For each of the 9 EIGRP labs, change `refresh_lab.py` to:
1. Reference `initial-configs/Rx.cfg` instead of `solutions/Rx.cfg`.
2. Update the closing print message from "Solution state" to "initial config state".

## Files to Modify (9 total)

| Lab | File |
|-----|------|
| 01 | `labs/eigrp/lab-01-basic-adjacency/scripts/refresh_lab.py` |
| 02 | `labs/eigrp/lab-02-path-selection/scripts/refresh_lab.py` |
| 03 | `labs/eigrp/lab-03-route-summarization/scripts/refresh_lab.py` |
| 04 | `labs/eigrp/lab-04-stub-wan-opt/scripts/refresh_lab.py` |
| 05 | `labs/eigrp/lab-05-authentication-advanced/scripts/refresh_lab.py` |
| 06 | `labs/eigrp/lab-06-filtering-control/scripts/refresh_lab.py` |
| 07 | `labs/eigrp/lab-07-redistribution/scripts/refresh_lab.py` |
| 08 | `labs/eigrp/lab-08-eigrp-over-vpn/scripts/refresh_lab.py` |
| 09 | `labs/eigrp/lab-09-dual-stack-migration/scripts/refresh_lab.py` |

## Acceptance Criteria

- [ ] All 9 scripts reference `initial-configs/Rx.cfg` paths.
- [ ] Closing print says "initial config state" instead of "Solution state".
- [ ] No changes to `push_config` logic or device lists.
