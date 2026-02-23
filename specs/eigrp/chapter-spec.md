# EIGRP Chapter Spec

## Exam Bullets Covered

- 1.9 Troubleshoot EIGRP (classic and named mode)
  - 1.9.a Address families (IPv4, IPv6)
  - 1.9.b Neighbor adjacency
  - 1.9.c Loop-free path selection (RD, FD, FC, successor, feasible successor)
  - 1.9.d Stubs
  - 1.9.e Load balancing (equal-cost, unequal-cost)
  - 1.9.f Metrics
- 1.1 Administrative distance (EIGRP context)
- 1.2 Route maps (EIGRP filtering, tagging)
- 1.3 Loop prevention (split horizon, route poisoning, EIGRP-specific)
- 1.5 Manual and auto-summarization (EIGRP)

## Preferences

<!-- Optional — high-level constraints or requests. Leave blank for defaults. -->
<!-- Examples: "6 labs max", "heavy troubleshooting focus", "skip IPv6" -->

## Generated Plan

> Populated by `chapter-topics` skill on 2026-02-23. Source: `labs/eigrp/baseline.yaml`

### Topology

R1 (c7200 Hub/Core) ↔ R2 (c3725 Branch A) ↔ R3 (c3725 Branch B) — triangle.
R4 (c3725 Stub/Edge) connects to R1 only, activated from Lab 06.

- Links: L1 (R1-R2), L2 (R1-R3), L3 (R2-R3), L4 (R1-R4 optional)
- IPv4: 10.x.0.0/30 transit, 10.0.0.x/32 loopbacks
- IPv6: 2001:db8:x::/64 transit, 2001:db8::x/128 loopbacks

### Lab Progression

| # | Title | Difficulty | Time | Blueprint | Devices |
|---|---|---|---|---|---|
| 01 | Classic Mode Adjacency | Foundation | 60 min | 1.9.b | R1, R2, R3 |
| 02 | Named Mode & Dual-Stack IPv6 | Foundation | 75 min | 1.9.a, 1.9.b | R1, R2, R3 |
| 03 | Metrics & K-Values | Intermediate | 90 min | 1.9.f | R1, R2, R3 |
| 04 | Feasible Successor & Unequal-Cost LB | Intermediate | 90 min | 1.9.c, 1.9.e | R1, R2, R3 |
| 05 | Summarization | Intermediate | 75 min | 1.5 | R1, R2, R3 |
| 06 | Stub Routing | Intermediate | 60 min | 1.9.d | R1, R2, R3, R4 |
| 07 | Filtering & Route Maps | Advanced | 90 min | 1.2, 1.3 | R1, R2, R3, R4 |
| 08 | AD & Split Horizon | Advanced | 75 min | 1.1, 1.3 | R1, R2, R3, R4 |
| 09 | Troubleshooting Integration | Advanced | 120 min | All | R1, R2, R3, R4 |

### Blueprint Coverage

| Blueprint | Lab(s) |
|---|---|
| 1.9.a Address families | 02 |
| 1.9.b Neighbor adjacency | 01, 02 |
| 1.9.c Loop-free path selection | 04 |
| 1.9.d Stubs | 06 |
| 1.9.e Load balancing | 04 |
| 1.9.f Metrics | 03 |
| 1.1 Administrative distance | 08 |
| 1.2 Route maps | 07 |
| 1.3 Loop prevention | 07, 08 |
| 1.5 Summarization | 05 |

## Notes

- EIGRP authentication is deferred to the Infrastructure Security chapter (Section 3.x)
- Classic mode (Lab 01) is taught first so students understand the legacy config before migrating to named mode (Lab 02)
- Lab 09 is a capstone troubleshooting lab covering all EIGRP blueprint bullets simultaneously
