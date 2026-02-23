# CCNP ENARSI (300-410) Exam Blueprint

## Exam Overview

- **Exam Code**: 300-410 ENARSI
- **Full Name**: Implementing Cisco Enterprise Advanced Routing and Services
- **Duration**: 90 minutes
- **Prerequisite**: None (but ENCOR 350-401 required for CCNP certification)

---

## Domain 1: Layer 3 Technologies (35%)

### 1.1 Troubleshoot administrative distance (all routing protocols)
### 1.2 Troubleshoot route map for any routing protocol (attributes, tagging, filtering)
### 1.3 Troubleshoot loop prevention mechanisms (filtering, tagging, split horizon, route poisoning)
### 1.4 Troubleshoot redistribution between any pair of routing protocols or routing protocol instances
### 1.5 Troubleshoot manual and auto-summarization with any routing protocol

### 1.6 Configure and verify policy-based routing
### 1.7 Configure and verify VRF-Lite
### 1.8 Describe Bidirectional Forwarding Detection (BFD)

### 1.9 Troubleshoot EIGRP (classic and named mode)
- 1.9.a Address families (IPv4, IPv6)
- 1.9.b Neighbor adjacency
- 1.9.c Loop-free path selection (RD, FD, FC, successor, feasible successor)
- 1.9.d Stubs
- 1.9.e Load balancing (equal-cost, unequal-cost)
- 1.9.f Metrics

### 1.10 Troubleshoot OSPF (v2/v3)
- 1.10.a Address families (IPv4, IPv6)
- 1.10.b Neighbor adjacency
- 1.10.c Path preference
- 1.10.d Operations (LSA types, area types, timers)

### 1.11 Troubleshoot BGP (Internal and External)
- 1.11.a Address families (IPv4, IPv6)
- 1.11.b Neighbor adjacency
- 1.11.c Loop prevention (AS path manipulation)
- 1.11.d Path selection (attributes and best-path)

---

## Domain 2: VPN Technologies (20%)

### 2.1 Describe MPLS operations (label stacking, LSR, LDP)
### 2.2 Describe MPLS Layer 3 VPN
### 2.3 Configure and verify DMVPN (single hub)
- 2.3.a GRE/mGRE
- 2.3.b NHRP
- 2.3.c IPsec
- 2.3.d Dynamic routing

### 2.4 Configure and verify FlexVPN (single hub) — TA only

---

## Domain 3: Infrastructure Security (20%)

### 3.1 Troubleshoot device security using IOS AAA (TACACS+, RADIUS, local database)
### 3.2 Troubleshoot router security features
- 3.2.a IPv4 access control lists (standard, extended, time-based)
- 3.2.b IPv6 traffic filter
- 3.2.c Unicast Reverse Path Forwarding (uRPF)

### 3.3 Troubleshoot control plane policing (CoPP) (concept, configuration)
### 3.4 Describe IPv6 First Hop Security features (RA Guard, DHCP Guard, binding table, ND inspection/snooping, source guard)

---

## Domain 4: Infrastructure Services (25%)

### 4.1 Troubleshoot device management
- 4.1.a Console and VTY
- 4.1.b Telnet, HTTP, HTTPS, SSH, SCP
- 4.1.c (T)FTP

### 4.2 Troubleshoot SNMP (v2c, v3)
### 4.3 Troubleshoot network problems using logging (local, syslog, debugs, conditional debugs, timestamps)

### 4.4 Troubleshoot IPv4 and IPv6 DHCP (client, IOS DHCP server, DHCP relay)
### 4.5 Troubleshoot network performance issues using IP SLA (jitter, tracking objects)
### 4.6 Troubleshoot NetFlow (v5, v9, Flexible NetFlow)
### 4.7 Troubleshoot network problems using Cisco DNA Center assurance (path trace, monitoring)

---

## Chapter Mapping

| Spec Folder | Blueprint Sections | Status |
|---|---|---|
| `eigrp/` | 1.9, 1.1–1.5 (EIGRP-specific) | Planned |
| `ospf/` | 1.10, 1.1–1.5 (OSPF-specific) | Planned |
| `bgp/` | 1.11, 1.1–1.5 (BGP-specific) | Planned |
| `redistribution/` | 1.4, 1.2, 1.3, 1.6, 1.7, 1.8 | Planned |
| `vpn/` | 2.1–2.4 | Planned |
| `infrastructure-security/` | 3.1–3.4 | Planned |
| `infrastructure-services/` | 4.1–4.7 | Planned |
