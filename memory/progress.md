# Lab Progress

> This file is the source of truth for lab generation status.
> Update it after every lab session.

## Active Work

- **Chapter:** eigrp
- **Lab in progress:** —
- **Last completed lab:** 08
- **Next action:** Generate lab-09 (Capstone I) — clean slate from core_topology; all blueprint bullets
- **Platform finalized:** 2026-02-23 — all routers c7200 + IOS 15.3(3)XB12; named mode EIGRP throughout; spurious network statements removed

---

## EIGRP (300-410 Section 1.9, 1.1–1.5)

| Lab | Name | Status | Notes |
|-----|------|--------|-------|
| — | baseline.yaml | Approved | Generated 2026-02-23 — 10 labs (8 objective + 2 capstone), all c7200 + IOS 15.3(3)XB12, R1/R2/R3 core + R4 from lab-06 |
| 01 | Classic Adjacency | Approved | Foundation — 60 min, covers 1.9.b adjacency. Generated 2026-02-24. |
| 02 | Named Mode & Dual-Stack | Approved | Foundation — 75 min, covers 1.9.a-b dual-stack. Generated 2026-02-24. |
| 03 | Metrics & K-Values | Review Needed | Intermediate — 90 min, covers 1.9.f metrics. Generated 2026-02-25. |
| 04 | Feasible Successor | Approved | Intermediate — 90 min, covers 1.9.c-e loop-free path selection. Generated 2026-02-26. |
| 05 | Summarization | Approved | Intermediate — 75 min, covers 1.5 summarization. Generated 2026-02-27. Approved 2026-02-27. |
| 06 | Stub Routing | Approved | Intermediate — 60 min, covers 1.9.d stubs, introduces R4. Generated 2026-02-27. Approved 2026-02-27. |
| 07 | Filtering & Route Maps | Approved | Advanced — 90 min, covers 1.2-1.3 filtering & route-maps. Generated 2026-03-04. Approved 2026-03-05. |
| 08 | AD & Split Horizon | Approved | Advanced — 75 min, covers 1.1-1.3 AD & split horizon. Generated 2026-03-05. Approved 2026-03-05. |
| 09 | Capstone I — Full Protocol Mastery | Not generated | Advanced — 120 min, clean slate; all blueprint bullets; configuration challenge |
| 10 | Capstone II — Comprehensive Troubleshooting | Not generated | Advanced — 120 min, clean slate; 5+ concurrent faults; troubleshooting challenge |

---

## OSPF (300-410 Section 1.10, 1.1–1.5)

| Lab | Name | Status | Notes |
|-----|------|--------|-------|
| — | baseline.yaml | Review Needed | Generated 2026-03-06 (eval run — draft, not approved) — 10 labs (8 objective + 2 capstone), all c7200 + IOS 15.3(3)XB12, R1/R2/R3 core + R4 from lab-05 |
| 01 | OSPFv2 Neighbor Adjacency & Authentication | Not generated | Foundation — 60 min, covers 1.10.b |
| 02 | OSPFv3 Dual-Stack — IPv4 and IPv6 Address Families | Not generated | Foundation — 75 min, covers 1.10.a, 1.10.b |
| 03 | OSPF Network Types — Broadcast, Point-to-Point, and Non-Broadcast | Not generated | Intermediate — 90 min, covers 1.10.c, 1.10.c(i), 1.10.c(iii) |
| 04 | OSPF Area Types — Backbone, Stub, NSSA, and Totally Stub | Not generated | Intermediate — 90 min, covers 1.10.c(ii), 1.10.c(iii) |
| 05 | Multi-Area OSPF — ABR, ASBR, and Virtual Links | Not generated | Intermediate — 90 min, covers 1.10.c(ii), 1.10.c(iii), 1.10.c(iv); introduces R4 |
| 06 | OSPF Inter-Area Summarization & Type 3/5 LSA Control | Not generated | Intermediate — 75 min, covers 1.5 |
| 07 | OSPF Route Filtering & Route Maps | Not generated | Advanced — 90 min, covers 1.2, 1.3 |
| 08 | OSPF Path Preference & Administrative Distance | Not generated | Advanced — 75 min, covers 1.10.d, 1.1 |
| 09 | Capstone I — Full Protocol Mastery | Not generated | Advanced — 120 min, clean slate; all blueprint bullets; configuration challenge |
| 10 | Capstone II — Comprehensive Troubleshooting | Not generated | Advanced — 120 min, clean slate; 5+ concurrent faults; troubleshooting challenge |

---

## BGP (300-410 Section 1.11)

| Lab | Name | Status | Notes |
|-----|------|--------|-------|
| — | baseline.yaml | Review Needed | Generated 2026-03-06 (eval run — draft, not approved) — 10 labs (8 objective + 2 capstone), all c7200 + IOS 15.3(3)XB12, R1/R2/R3 core + R5 from lab-02, R4 from lab-04 |
| 01 | eBGP Peering Fundamentals | Not generated | Foundation — 60 min, covers 1.11, 1.11.b |
| 02 | iBGP, Full-Mesh & Route Reflector | Not generated | Foundation — 75 min, covers 1.11.b, 1.11.d; introduces R5 |
| 03 | BGP Address Families — IPv4 Unicast & IPv6 | Not generated | Intermediate — 75 min, covers 1.11.a, 1.11.b |
| 04 | BGP Path Attributes & Best-Path Selection | Not generated | Intermediate — 90 min, covers 1.11.b, 1.11.c; introduces R4 |
| 05 | BGP Authentication, Peer Groups & Timers | Not generated | Intermediate — 75 min, covers 1.11.b |
| 06 | BGP Policies — Inbound/Outbound Filtering & Route Maps | Not generated | Advanced — 90 min, covers 1.11.e, 1.2 |
| 07 | BGP Communities & AS-Path Loop Prevention | Not generated | Advanced — 90 min, covers 1.3, 1.11.c, 1.11.e |
| 08 | BGP Administrative Distance & VRF-Lite | Not generated | Advanced — 90 min, covers 1.1, 1.11 |
| 09 | Capstone I — BGP Full Protocol Mastery | Not generated | Advanced — 120 min, clean slate; all blueprint bullets |
| 10 | Capstone II — BGP Comprehensive Troubleshooting | Not generated | Advanced — 120 min, clean slate; 5+ concurrent faults |

---

## Redistribution (300-410 Sections 1.4, 1.6–1.8)

| Lab | Name | Status | Notes |
|-----|------|--------|-------|
| — | baseline.yaml | Not generated | Run `chapter-topics` first |

---

## VPN (300-410 Sections 2.1–2.3)

| Lab | Name | Status | Notes |
|-----|------|--------|-------|
| — | baseline.yaml | Review Needed | Generated 2026-03-06 (eval run — draft, not approved) — 7 labs (5 objective + 2 capstone), all c7200 + IOS 15.3(3)XB12, R1/R2/R3 core + R4 from lab-03 |
| 01 | GRE Tunnel Foundations | Not generated | Foundation — 60 min, covers 2.3.a GRE |
| 02 | DMVPN Phase 1 — mGRE and NHRP | Not generated | Foundation — 75 min, covers 2.3.a-b |
| 03 | DMVPN Phase 2 — Spoke-to-Spoke Traffic | Not generated | Intermediate — 90 min, covers 2.3.a-b, 2.3.d-e; introduces R4 |
| 04 | IPsec Profile over DMVPN | Not generated | Intermediate — 90 min, covers 2.3.a-e |
| 05 | MPLS Theory Lab — Operations and L3 VPN Concepts | Not generated | Foundation — 60 min, describe-only, covers 2.1-2.2 |
| 06 | DMVPN Full Protocol Mastery — Capstone I | Not generated | Advanced — 120 min, clean slate; all blueprint bullets |
| 07 | DMVPN Comprehensive Troubleshooting — Capstone II | Not generated | Advanced — 120 min, clean slate; 5+ concurrent faults |

---

## Infrastructure Security (300-410 Sections 3.1–3.4)

| Lab | Name | Status | Notes |
|-----|------|--------|-------|
| — | baseline.yaml | Not generated | Run `chapter-topics` first |

---

## Infrastructure Services (300-410 Sections 4.1–4.7)

| Lab | Name | Status | Notes |
|-----|------|--------|-------|
| — | baseline.yaml | Not generated | Run `chapter-topics` first |

---

## Status Key

| Symbol | Meaning |
|--------|---------|
| Not generated | No files created yet |
| In Progress | Currently being built |
| Review Needed | Generated — awaiting user approval |
| Approved | Reviewed and approved — ready to chain |
| Complete | Approved + fault-injection scripts done |
