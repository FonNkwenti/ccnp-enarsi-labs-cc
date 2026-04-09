# CCNP ENARSI 300-410 Lab Workbooks

Hands-on lab workbooks for the Cisco **CCNP ENARSI (300-410)** exam — *Implementing Cisco Enterprise Advanced Routing and Services*.

Labs run on **GNS3 with Dynamips** (c7200, IOS 15.3(3)XB12) — fully compatible with Apple Silicon.
Each lab follows the [DeepSeek Standard](docs/README.md): workbook + topology diagram + initial configs + solution configs + fault-injection scripts.

## Chapters

| Chapter | Blueprint Sections |
|---|---|
| EIGRP | 1.9, 1.1–1.5 |
| OSPF | 1.10, 1.1–1.5 |
| BGP | 1.11, 1.1–1.5 |
| Redistribution | 1.4, 1.2, 1.3, 1.6–1.8 |
| VPN | 2.1–2.4 |
| Infrastructure Security | 3.1–3.4 |
| Infrastructure Services | 4.1–4.7 |

## Lab Progress

> Auto-updated after each lab session. Do not edit manually.
> Source of truth: `memory/progress.md`
>
> Legend: `✓` Approved · `◉` Review Needed · `⊙` In Progress · `○` Not Generated

```mermaid
mindmap
  root((CCNP ENARSI 300-410))
    EIGRP 1.9 1.1-1.5
      ✓ baseline.yaml
      ✓ Lab 01 Classic Adjacency
      ✓ Lab 02 Named Mode and Dual-Stack
      ◉ Lab 03 Metrics and K-Values
      ✓ Lab 04 Feasible Successor
      ✓ Lab 05 Summarization
      ✓ Lab 06 Stub Routing
      ✓ Lab 07 Filtering and Route Maps
      ✓ Lab 08 AD and Split Horizon
      ○ Lab 09 Capstone I
      ○ Lab 10 Capstone II
    OSPF 1.10 1.1-1.5
      ✓ baseline.yaml
      ○ Lab 01 OSPFv2 Neighbor Adjacency and Authentication
      ○ Lab 02 OSPFv3 Dual-Stack IPv4 and IPv6 Address Families
      ○ Lab 03 OSPF Network Types Broadcast Point-to-Point and Non-Broadcast
      ○ Lab 04 OSPF Area Types Backbone Stub NSSA and Totally Stub
      ○ Lab 05 Multi-Area OSPF ABR ASBR and Virtual Links
      ○ Lab 06 OSPF Inter-Area Summarization and Type 3 5 LSA Control
      ○ Lab 07 OSPF Route Filtering and Route Maps
      ○ Lab 08 OSPF Path Preference and Administrative Distance
      ○ Lab 09 Capstone I
      ○ Lab 10 Capstone II
    BGP 1.11
      ✓ baseline.yaml
      ○ Lab 01 eBGP Peering Fundamentals
      ○ Lab 02 iBGP Full-Mesh and Route Reflector
      ○ Lab 03 BGP Address Families IPv4 and IPv6
      ○ Lab 04 BGP Path Attributes and Best-Path Selection
      ○ Lab 05 BGP Authentication Peer Groups and Timers
      ○ Lab 06 BGP Policies Filtering and Route Maps
      ○ Lab 07 BGP Communities and AS-Path Loop Prevention
      ○ Lab 08 BGP Administrative Distance and VRF-Lite
      ○ Lab 09 Capstone I
      ○ Lab 10 Capstone II
    Redistribution 1.4 1.6-1.8
      ○ baseline.yaml
    VPN 2.1-2.3
      ✓ baseline.yaml
      ○ Lab 01 GRE Tunnel Foundations
      ○ Lab 02 DMVPN Phase 1 mGRE and NHRP
      ○ Lab 03 DMVPN Phase 2 Spoke-to-Spoke Traffic
      ○ Lab 04 IPsec Profile over DMVPN
      ○ Lab 05 MPLS Theory Lab
      ○ Lab 06 Capstone I
      ○ Lab 07 Capstone II
    Infrastructure Security 3.1-3.4
      ○ baseline.yaml
    Infrastructure Services 4.1-4.7
      ○ baseline.yaml
```
