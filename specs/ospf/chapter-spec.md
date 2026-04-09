# OSPF Chapter Spec

## Exam Bullets Covered

- 1.10 Troubleshoot OSPF (v2/v3)
  - 1.10.a Address families (IPv4, IPv6)
  - 1.10.b Neighbor adjacency
  - 1.10.c Path preference
  - 1.10.d Operations (LSA types, area types, timers)
- 1.1 Administrative distance (OSPF context)
- 1.2 Route maps (OSPF filtering)
- 1.3 Loop prevention (OSPF-specific)
- 1.5 Manual and auto-summarization (OSPF inter-area)

## Preferences

<!-- Optional — high-level constraints or requests. Leave blank for defaults. -->
<!-- Examples: "6 labs max", "heavy troubleshooting focus", "skip OSPFv3" -->

## Generated Plan

> Generated 2026-03-06 by claude-sonnet-4-6 using the chapter-topics skill.

### Topology Summary

The OSPF chapter uses a 4-router topology built around a 3-router Area 0 backbone triangle (R1, R2, R3) with an optional Area 1 leaf (R4, introduced in lab-05). R1 acts as ABR between Area 0 and Area 1. R3 acts as ABR between Area 0 and Area 2 (simulated via loopback in early labs, physical in capstones). R2 is the internal backbone peer and ASBR target for redistribution labs. All routers are c7200 (IOS 15.3(3)XB12) to support OSPFv3 address families and dual-stack. R4 is pre-reserved from the start but activated from lab-05 onward.

### Lab Progression

| # | Title | Difficulty | Time | Blueprint Bullets | Devices |
|---|-------|-----------|------|-------------------|---------|
| 01 | OSPFv2 Neighbor Adjacency & Authentication | Foundation | 60 min | 1.10.b | R1, R2, R3 |
| 02 | OSPFv3 Dual-Stack — IPv4 and IPv6 Address Families | Foundation | 75 min | 1.10.a, 1.10.b | R1, R2, R3 |
| 03 | OSPF Network Types — Broadcast, Point-to-Point, and Non-Broadcast | Intermediate | 90 min | 1.10.c, 1.10.c(i), 1.10.c(iii) | R1, R2, R3 |
| 04 | OSPF Area Types — Backbone, Stub, NSSA, and Totally Stub | Intermediate | 90 min | 1.10.c(ii), 1.10.c(iii) | R1, R2, R3 |
| 05 | Multi-Area OSPF — ABR, ASBR, and Virtual Links | Intermediate | 90 min | 1.10.c(ii), 1.10.c(iii), 1.10.c(iv) | R1, R2, R3, R4 |
| 06 | OSPF Inter-Area Summarization & Type 3/5 LSA Control | Intermediate | 75 min | 1.5 | R1, R2, R3, R4 |
| 07 | OSPF Route Filtering & Route Maps | Advanced | 90 min | 1.2, 1.3 | R1, R2, R3, R4 |
| 08 | OSPF Path Preference & Administrative Distance | Advanced | 75 min | 1.10.d, 1.1 | R1, R2, R3, R4 |
| 09 | OSPF Full Protocol Mastery — Capstone I | Advanced | 120 min | All | R1, R2, R3, R4 |
| 10 | OSPF Comprehensive Troubleshooting — Capstone II | Advanced | 120 min | All | R1, R2, R3, R4 |

### Blueprint Coverage

| Exam Bullet | Description | Covered By |
|-------------|-------------|------------|
| 1.10 | Troubleshoot OSPF (v2/v3) | All labs |
| 1.10.a | Address families (IPv4, IPv6) | Lab 02, 09, 10 |
| 1.10.b | Neighbor relationship and authentication | Lab 01, 02, 09, 10 |
| 1.10.c | Network types, area types, and router types | Lab 03, 04, 05, 09, 10 |
| 1.10.c(i) | Point-to-point, multipoint, broadcast, nonbroadcast | Lab 03, 09, 10 |
| 1.10.c(ii) | Area types: backbone, normal, stub, NSSA, totally stub | Lab 04, 05, 09, 10 |
| 1.10.c(iii) | Internal router, backbone router, ABR, ASBR | Lab 03, 04, 05, 09, 10 |
| 1.10.c(iv) | Virtual link | Lab 05, 09, 10 |
| 1.10.d | Path preference | Lab 08, 09, 10 |
| 1.1 | Administrative distance | Lab 08, 09, 10 |
| 1.2 | Route maps (filtering, tagging) | Lab 07, 09, 10 |
| 1.3 | Loop prevention (filtering, tagging) | Lab 07, 09, 10 |
| 1.5 | Manual and auto-summarization | Lab 06, 09, 10 |

## Notes

<!-- Any chapter-specific constraints or decisions -->
