# VPN Technologies Chapter Spec

## Exam Bullets Covered

- 2.1 Describe MPLS operations (label stacking, LSR, LDP)
- 2.2 Describe MPLS Layer 3 VPN
- 2.3 Configure and verify DMVPN (single hub)
  - 2.3.a GRE/mGRE
  - 2.3.b NHRP
  - 2.3.c IPsec
  - 2.3.d Dynamic routing
- 2.4 Configure and verify FlexVPN (single hub)

## Preferences

DMVPN is the core focus — all DMVPN components (GRE/mGRE, NHRP, IPsec) get proper coverage.
MPLS topics (2.1, 2.2) are describe-only.

## Generated Plan

> Generated 2026-03-06 by claude-sonnet-4-6 using chapter-topics skill.

### Topology Summary

Core topology: **R1** (Hub, c7200), **R2** (Spoke-A, c7200), **R3** (Spoke-B, c7200) — 3 routers active from Lab 01.
**R4** (Spoke-C, c7200) is introduced in Lab 03 to enable full spoke-to-spoke Phase 2 scenarios.
All routers use c7200 with IOS 15.3(3)XB12 (required for IPsec crypto engine support on Dynamips).
Underlay links simulate an Internet transport (10.0.12.0/30, 10.0.13.0/30, 10.0.14.0/30).
DMVPN overlay uses 172.16.0.0/24 on tunnel0 interfaces; loopbacks simulate branch LANs (192.168.N.0/24).

### Lab Progression

| # | Title | Difficulty | Time | Blueprint Bullets | Devices |
|---|-------|------------|------|-------------------|---------|
| 01 | GRE Tunnel Foundations | Foundation | 60 min | 2.3.a | R1, R2, R3 |
| 02 | DMVPN Phase 1 — mGRE and NHRP | Foundation | 75 min | 2.3.a, 2.3.b | R1, R2, R3 |
| 03 | DMVPN Phase 2 — Spoke-to-Spoke Traffic | Intermediate | 90 min | 2.3.a, 2.3.b, 2.3.d, 2.3.e | R1, R2, R3, R4 |
| 04 | IPsec Profile over DMVPN | Intermediate | 90 min | 2.3.a, 2.3.b, 2.3.c, 2.3.d, 2.3.e | R1, R2, R3, R4 |
| 05 | MPLS Theory Lab — Operations and L3 VPN Concepts | Foundation | 60 min | 2.1, 2.2 | R1, R2, R3 |
| 06 | DMVPN Full Protocol Mastery — Capstone I | Advanced | 120 min | 2.1–2.3.e | R1, R2, R3, R4 |
| 07 | DMVPN Comprehensive Troubleshooting — Capstone II | Advanced | 120 min | 2.3.a–2.3.e | R1, R2, R3, R4 |

### Blueprint Coverage

| Exam Bullet | Description | Covered In |
|-------------|-------------|------------|
| 2.1 | Describe MPLS operations (LSR, LDP, label switching, LSP) | Lab 05, Cap I |
| 2.2 | Describe MPLS Layer 3 VPN | Lab 05, Cap I |
| 2.3 | Configure and verify DMVPN (single hub) | Labs 01–04, Cap I, Cap II |
| 2.3.a | GRE/mGRE | Labs 01–04, Cap I, Cap II |
| 2.3.b | NHRP | Labs 02–04, Cap I, Cap II |
| 2.3.c | IPsec | Lab 04, Cap I, Cap II |
| 2.3.d | Dynamic neighbor | Labs 03–04, Cap I, Cap II |
| 2.3.e | Spoke-to-spoke | Labs 03–04, Cap I, Cap II |

### Design Notes

- **MPLS (2.1, 2.2)** are describe-only exam bullets. Lab 05 is a theory lab with no live config; workbook content covers label stacking, LSP establishment, and L3 VPN architecture. Placed after the DMVPN hands-on sequence so students complete the practical work first.
- **FlexVPN (2.4)** does not appear in the official 300-410 v1.1 blueprint (July 2025 version) and is therefore excluded.
- **All routers use c7200** — IPsec crypto engine requires c7200 on Dynamips; c3725 is not used in this chapter.
- **Capstone I** starts from a clean slate (IP addressing only) — not chained from Lab 04 solutions.
- **Capstone II** starts from a clean slate (IP addressing only) — pre-broken network with 5+ concurrent faults.

## Notes

- MPLS topics (2.1, 2.2) are describe-only on the exam — theory labs, not config labs
- DMVPN (2.3) is the primary hands-on focus
- FlexVPN and IPsec require c7200 for crypto support on Dynamips
