# BGP Chapter Spec

## Exam Bullets Covered

- 1.11 Troubleshoot BGP (Internal and External)
  - 1.11.a Address families (IPv4, IPv6)
  - 1.11.b Neighbor adjacency
  - 1.11.c Loop prevention (AS path manipulation)
  - 1.11.d Path selection (attributes and best-path)
- 1.1 Administrative distance (BGP context)
- 1.2 Route maps (BGP attributes, tagging, filtering)
- 1.3 Loop prevention (BGP AS-path, communities)

## Preferences

<!-- Optional — high-level constraints or requests. Leave blank for defaults. -->
<!-- Examples: "include iBGP + eBGP", "focus on path selection attributes" -->

## Generated Plan

> Generated 2026-03-06 by chapter-topics-creator skill (claude-sonnet-4-6).

### Topology Summary

Five routers across three autonomous systems: R1 and R2 (and R5, optional from lab-02) are iBGP peers in AS 65001, with R1 acting as Route Reflector from lab-02 onward. R3 (AS 65002) is an eBGP peer to R1, providing an external AS for eBGP fundamentals and policy labs. R4 (AS 65003, optional from lab-04) adds a second external AS enabling dual-path scenarios for path attribute comparison and community manipulation. All routers use c7200 (IOS 15.3(3)XB12) on Dynamips.

Core devices (labs 01–10): R1, R2, R3.
Optional: R5 (iBGP/RR client, from lab-02), R4 (eBGP AS 65003, from lab-04).
Total devices at full scale: 5 (within 3–15 limit).

### Lab Progression

| # | Title | Difficulty | Time | Blueprint Bullets | Devices |
|---|-------|-----------|------|-------------------|---------|
| 01 | eBGP Peering Fundamentals | Foundation | 60 min | 1.11, 1.11.b | R1, R3 |
| 02 | iBGP, Full-Mesh & Route Reflector | Foundation | 75 min | 1.11.b, 1.11.d | R1, R2, R3, R5 |
| 03 | BGP Address Families — IPv4 Unicast & IPv6 | Intermediate | 75 min | 1.11.a, 1.11.b | R1, R2, R3, R5 |
| 04 | BGP Path Attributes & Best-Path Selection | Intermediate | 90 min | 1.11.b, 1.11.c | R1, R2, R3, R4, R5 |
| 05 | BGP Authentication, Peer Groups & Timers | Intermediate | 75 min | 1.11.b | R1, R2, R3, R4, R5 |
| 06 | BGP Policies — Inbound/Outbound Filtering & Route Maps | Advanced | 90 min | 1.11.e, 1.2 | R1, R2, R3, R4, R5 |
| 07 | BGP Communities & AS-Path Loop Prevention | Advanced | 90 min | 1.3, 1.11.c, 1.11.e | R1, R2, R3, R4, R5 |
| 08 | BGP Administrative Distance & VRF-Lite | Advanced | 90 min | 1.1, 1.11 | R1, R2, R3, R4, R5 |
| 09 | BGP Full Protocol Mastery — Capstone I | Advanced | 120 min | All | R1, R2, R3, R4, R5 |
| 10 | BGP Comprehensive Troubleshooting — Capstone II | Advanced | 120 min | All | R1, R2, R3, R4, R5 |

### Blueprint Coverage

| Blueprint Bullet | Covered In |
|-----------------|-----------|
| 1.11 Troubleshoot BGP (Internal and External; unicast and VRF-lite) | Lab 01, 02, 08 |
| 1.11.a Address families (IPv4, IPv6) | Lab 03 |
| 1.11.b Neighbor relationship and authentication (next-hop, multihop, 4-byte AS, private AS, route refresh, synchronization, operation, peer group, states and timers) | Lab 01, 02, 03, 04, 05 |
| 1.11.c Path preference (attributes and best-path) | Lab 04, 07 |
| 1.11.d Route reflector | Lab 02 |
| 1.11.e Policies (inbound/outbound filtering, path manipulation) | Lab 06, 07 |
| 1.1 Administrative distance (BGP) | Lab 08 |
| 1.2 Route maps (BGP attributes, tagging, filtering) | Lab 06 |
| 1.3 Loop prevention (AS-path, communities) | Lab 07 |

### Preferences Honored

No explicit preferences were provided in the `## Preferences` section. Defaults applied: iBGP + eBGP both covered, path selection attributes given dedicated lab (lab-04), Route Reflector introduced early (lab-02) per ENARSI blueprint emphasis on 1.11.d.

## Notes

<!-- Any chapter-specific constraints or decisions -->
