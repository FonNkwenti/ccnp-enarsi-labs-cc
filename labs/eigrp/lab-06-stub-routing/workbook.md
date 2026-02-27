# ENARSI Lab 06: EIGRP Stub Routers

**Difficulty:** Intermediate | **Estimated Time:** 60 minutes | **Blueprint:** 1.9.d

## Table of Contents

1. [Concepts & Skills Covered](#1-concepts--skills-covered)
2. [Topology & Scenario](#2-topology--scenario)
3. [Hardware & Environment Specifications](#3-hardware--environment-specifications)
4. [Base Configuration](#4-base-configuration)
5. [Lab Challenge: Core Implementation](#5-lab-challenge-core-implementation)
6. [Verification & Analysis](#6-verification--analysis)
7. [Verification Cheatsheet](#7-verification-cheatsheet)
8. [Solutions (Spoiler Alert!)](#8-solutions-spoiler-alert)
9. [Troubleshooting Scenarios](#9-troubleshooting-scenarios)
10. [Lab Completion Checklist](#10-lab-completion-checklist)

---

## 1. Concepts & Skills Covered

**Exam Objective:** 1.9.d — EIGRP Stubs

EIGRP stub routing is one of the most important scalability and stability features in the ENARSI blueprint. Without stubs, every topology change in an EIGRP domain can trigger a flood of query messages that propagates to every router in the AS — potentially causing convergence delays or Stuck-in-Active conditions. Stub routing constrains which routers participate in the query process, shrinking the Active Query Boundary and protecting hub-and-spoke and edge deployments.

### What Is an EIGRP Stub Router?

A stub router declares to its EIGRP neighbors that it is a leaf node in the topology — it provides limited reachability (usually only its directly connected and summary prefixes) and should never be used as a transit path. Once a router advertises stub status, its neighbors:

1. **Stop sending queries** to the stub router during topology changes — the stub is excluded from the query scope.
2. **Suppress routes** through the stub — no other router will use the stub as a transit next-hop.

The stub flag is carried in the EIGRP Hello packet as a TLV. You can verify it with `show ip eigrp neighbors detail`, which displays `Stub Peer Advertising` for any stub-configured neighbor.

> **Critical distinction:** A stub router still receives a full routing table from its non-stub neighbor (the hub). The restriction applies to what it *advertises* outbound, not what it *receives* inbound. This is often misunderstood on the exam.

### EIGRP Stub Router Types

The `eigrp stub` command accepts one or more keyword arguments that control which routes R4 will advertise to its EIGRP neighbors:

| Keyword | Routes Advertised | Typical Use |
|---------|-------------------|-------------|
| `connected` | Directly connected interfaces under EIGRP | Most common; advertise local subnets |
| `summary` | Manually configured summary addresses | Use with `ip summary-address eigrp` |
| `redistributed` | Routes redistributed into EIGRP from other protocols | Rare for true stubs |
| `receive-only` | **No routes advertised** — purely passive listener | Diagnostic; not for production stubs |
| `leak-map` | Routes explicitly permitted by a route-map | Fine-grained control over what leaks out |

Multiple keywords can be combined: `eigrp stub connected summary` is the most common production configuration. `receive-only` is mutually exclusive with all other keywords.

In Named Mode EIGRP (the mode used throughout this lab series), `eigrp stub` is configured **inside the address-family block**, not under the top-level `router eigrp` process:

```
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  eigrp stub connected summary
  ...
 exit-address-family
```

### Query Scoping and Stuck-in-Active Prevention

When an EIGRP route loses its Feasible Successor and enters Active state, the router sends query messages to all EIGRP neighbors asking "do you have an alternative path?" Each neighbor must reply before the router can exit Active state. If a neighbor doesn't reply within the Active Timer (default 3 minutes), the route enters **Stuck-in-Active (SIA)** state — an EIGRP emergency that tears down the neighbor relationship.

In a large network, queries can propagate many hops away from the origin. Each intermediate router must wait for all of its own neighbors to reply before replying upstream. This chain reaction is called **query propagation** and can extend convergence times drastically.

Stub routing solves this by creating an **Active Query Boundary**: when a hub router detects that a neighbor is flagged as a stub, it does not send queries to that neighbor. The stub is simply excluded from the query/reply cycle. This limits convergence impact to the non-stub portion of the network.

```
Without Stub:                      With Stub (eigrp stub connected summary):
R1 ──query──> R2                   R1  ────────────────────────────────>  No query sent to R4
R1 ──query──> R3                   R1 ──query──> R2
R1 ──query──> R4 (stub candidate)  R1 ──query──> R3
R4 must reply before R1 converges  R1 converges without waiting for R4
```

### Hub-and-Spoke Design Considerations

EIGRP stub routing is architecturally designed for hub-and-spoke topologies where:
- The **hub** (R1) is a full EIGRP participant with multiple peers
- The **spoke/edge** (R4) has only one uplink to the hub and no redundant paths

Configuring a router with multiple EIGRP peers as a stub would be a misconfiguration — those peers would never receive queries that they legitimately need to answer. Always verify that a candidate stub router has **only one EIGRP neighbor** (the hub) before applying the stub command.

**Skills this lab develops:**

| Skill | Description |
|-------|-------------|
| Stub router configuration (Named Mode) | Configure `eigrp stub` inside an address-family block |
| Active Query Boundary validation | Verify `show ip eigrp neighbors detail` shows stub flag |
| Stub advertisement behavior | Distinguish what a stub advertises vs. receives |
| Stub troubleshooting | Diagnose passive interface, stub type, and missing network statement faults |

---

## 2. Topology & Scenario

As the lead network engineer at Acme Corp, you are expanding the EIGRP WAN to support a new edge office. The existing hub-and-spoke topology connects headquarters (R1) to Branch-A (R2) and Branch-B (R3). A fourth router, R4, has just been physically installed at a small satellite office connected solely to R1 via a dedicated link.

R4 hosts a local LAN (192.168.4.0/24) used by edge workstations. Because R4 connects only to R1 and has no redundant paths, it must be configured as an **EIGRP stub router** — it should advertise its connected and summary prefixes, but it must never be treated as a transit point and must not participate in EIGRP query propagation.

Your task is to bring R4 into the EIGRP domain and apply the correct stub configuration.

```
         ┌────────────────────────────┐               ┌───────────────────────────┐
         │            R1              ├── Fa1/1 ──── Fa0/0                        │
         │        (Hub / Core)        │  .1      .2  │          R4               │
         │    Lo0: 10.0.0.1/32        │  10.14.0.0/30│      (Stub / Edge)        │
         └──────┬──────────────┬──────┘               │  Lo0: 10.0.0.4/32        │
      Fa0/0     │              │  Fa1/0               │  Lo1: 192.168.4.1/24     │
10.12.0.1/30    │              │  10.13.0.1/30        └───────────────────────────┘
                │              │
10.12.0.2/30    │              │  10.13.0.2/30
      Fa0/0     │              │  Fa0/0
         ┌──────┘              └──────────────┐
         │                                   │
┌────────┴──────────────┐   ┌────────────────┴────────────┐
│         R2            │   │           R3                │
│     (Branch A)        │   │       (Branch B)            │
│  Lo0: 10.0.0.2/32     │   │  Lo0: 10.0.0.3/32          │
│  Lo1: 172.16.20.1/24  │   │  Lo1: 172.16.30.1/24       │
│  Lo2: 172.16.21.1/24  │   │  Lo2: 172.16.31.1/24       │
└──────────┬────────────┘   └────────────┬────────────────┘
       Fa0/1│                            │Fa0/1
  10.23.0.1/30│                        │10.23.0.2/30
              └────────────────────────┘
                       10.23.0.0/30
```

> **Note on summarization (inherited from Lab 05):** R2 advertises a manual summary `172.16.20.0/23` covering Lo1 and Lo2. R3 advertises `172.16.30.0/23`. These summaries remain active throughout this lab.

---

## 3. Hardware & Environment Specifications

**Platform:** Cisco c7200 | **IOS:** 15.3(3)XB12 | **EIGRP Mode:** Named Mode (AS 100)

### Cabling Table

| Link ID | Source | Interface | Target | Interface | Subnet IPv4 |
|---------|--------|-----------|--------|-----------|-------------|
| L1 | R1 | Fa0/0 | R2 | Fa0/0 | 10.12.0.0/30 |
| L2 | R1 | Fa1/0 | R3 | Fa0/0 | 10.13.0.0/30 |
| L3 | R2 | Fa0/1 | R3 | Fa0/1 | 10.23.0.0/30 |
| L4 | R1 | Fa1/1 | R4 | Fa0/0 | 10.14.0.0/30 |

### Console Access Table

| Device | Role | Console Port | Connection Command |
|--------|------|-------------|-------------------|
| R1 | Hub / Core | 5001 | `telnet 127.0.0.1 5001` |
| R2 | Branch A | 5002 | `telnet 127.0.0.1 5002` |
| R3 | Branch B | 5003 | `telnet 127.0.0.1 5003` |
| R4 | Stub / Edge | 5004 | `telnet 127.0.0.1 5004` |

### Adapter Card Reference

| Router | Slot 0 | Slot 1 | Relevant Interfaces |
|--------|--------|--------|---------------------|
| R1 | C7200-IO-FE | PA-2FE-TX | Fa0/0, Fa1/0, Fa1/1 |
| R2 | C7200-IO-2FE | — | Fa0/0, Fa0/1 |
| R3 | C7200-IO-2FE | — | Fa0/0, Fa0/1 |
| R4 | C7200-IO-FE | — | Fa0/0 |

---

## 4. Base Configuration

Run `python3 setup_lab.py` to push the initial-configs to all four routers before starting.

### Pre-configured in initial-configs/

- Hostnames, `no ip domain-lookup`, `ipv6 unicast-routing` on all routers
- All interface IP addresses (IPv4 and IPv6) and `no shutdown`
- EIGRP Named Mode (AS 100) fully operational on **R1, R2, and R3** — neighbors R1↔R2, R1↔R3, R2↔R3 are already established
- Manual summarization on R2 and R3 (inherited from Lab 05): `172.16.20.0/23` and `172.16.30.0/23`
- R1 `fa1/1` interface **is configured** with IP addressing and is administratively up — the physical cable to R4 is in place
- R4 **interfaces are configured** with IP addresses (Fa0/0, Lo0, Lo1) and are up

### NOT pre-configured — Student must configure

- EIGRP routing process on R4
- Subnet advertisement (network statements) on R4
- R1 EIGRP network statement for the R4-facing link (Fa1/1)
- Stub router declaration on R4

---

## 5. Lab Challenge: Core Implementation

### Task 1: Add R4 to the EIGRP Domain

- Enable EIGRP Named Mode (process name `ENARSI`, Autonomous System 100) on R4
- Configure R4's router ID to match its Loopback0 address
- Advertise R4's link to R1 (10.14.0.0/30), its router-ID loopback (10.0.0.4/32), and its stub LAN (192.168.4.0/24) into the IPv4 address family
- Configure the IPv6 address family on R4 using the same AS number and router ID
- Add R1's Fa1/1 subnet (10.14.0.0/30) to R1's IPv4 address family so that the R1↔R4 adjacency forms
- Disable auto-summary on R4

**Verification:** `show ip eigrp neighbors` on R1 must show three neighbors — R2, R3, **and R4**. `show ip eigrp neighbors` on R4 must show exactly one neighbor (R1 at 10.14.0.1). `show ip route eigrp` on R4 must include routes learned from the rest of the EIGRP domain.

---

### Task 2: Configure R4 as an EIGRP Stub Router

- Configure R4 to advertise only its connected and summary routes in the IPv4 address family — use the combination that covers both route types in a single command
- Apply the same stub setting to R4's IPv6 address family

**Verification:** `show ip eigrp neighbors detail` on R1 must show R4 with the line `Stub Peer Advertising (CONNECTED SUMMARY) Routes` and `Suppressing queries`. The stub flag must appear for R4 only — R2 and R3 are not stubs.

---

### Task 3: Verify Stub Router Behavior

- Confirm that R1, R2, and R3 have a route to R4's stub LAN (192.168.4.0/24) learned via EIGRP
- Confirm that R4's routing table contains routes received from the EIGRP domain (stub routers receive routes — they only restrict what they advertise)
- Verify that R4 is not in the EIGRP topology table of R2 or R3 as a transit next-hop — trace a path from R2 to R3's loopback and confirm it does not traverse R4

**Verification:** `show ip route 192.168.4.0` on R1, R2, and R3 must all return an EIGRP (`D`) route. `show ip eigrp topology all-links` on R1 must show R4 as a stub peer. `ping 192.168.4.1` from R2 must succeed.

---

## 6. Verification & Analysis

### Task 1: R1↔R4 Adjacency

```
R1# show ip eigrp neighbors
EIGRP-IPv4 VR(ENARSI) Address-Family Neighbors for AS(100)
H   Address         Interface       Hold Uptime   SRTT   RTO  Q  Seq
                                   (sec)          (ms)       Cnt Num
2   10.14.0.2       Fa1/1             13 00:02:04   11   200  0  4   ! ← R4 must appear on Fa1/1
1   10.13.0.2       Fa1/0             12 00:15:30   12   200  0  31
0   10.12.0.2       Fa0/0             11 00:15:35   10   200  0  28

R4# show ip eigrp neighbors
EIGRP-IPv4 VR(ENARSI) Address-Family Neighbors for AS(100)
H   Address         Interface       Hold Uptime   SRTT   RTO  Q  Seq
                                   (sec)          (ms)       Cnt Num
0   10.14.0.1       Fa0/0             14 00:02:04   11   200  0  35   ! ← R1 only; R4 sees exactly one neighbor

R4# show ip route eigrp
     10.0.0.0/32 is subnetted, 4 subnets
D       10.0.0.1/32 [90/130816] via 10.14.0.1, 00:01:50, FastEthernet0/0   ! ← R1 Lo0 reachable
D       10.0.0.2/32 [90/412416] via 10.14.0.1, 00:01:50, FastEthernet0/0
D       10.0.0.3/32 [90/412416] via 10.14.0.1, 00:01:50, FastEthernet0/0
     10.12.0.0/30 is subnetted, 1 subnets
D       10.12.0.0/30 [90/286720] via 10.14.0.1, 00:01:50, FastEthernet0/0
     10.13.0.0/30 is subnetted, 1 subnets
D       10.13.0.0/30 [90/286720] via 10.14.0.1, 00:01:50, FastEthernet0/0
     10.23.0.0/30 is subnetted, 1 subnets
D       10.23.0.0/30 [90/286720] via 10.14.0.1, 00:01:50, FastEthernet0/0
D    172.16.20.0/23 [90/412416] via 10.14.0.1, 00:01:50, FastEthernet0/0  ! ← R2 summary received
D    172.16.30.0/23 [90/412416] via 10.14.0.1, 00:01:50, FastEthernet0/0  ! ← R3 summary received
```

> **Key concept:** R4 receives the full EIGRP routing table from R1. Stub status restricts *outbound advertisements*, not inbound route reception. R4's routing table will look identical to a non-stub router with one neighbor.

### Task 2: Stub Flag Verification

```
R1# show ip eigrp neighbors detail
EIGRP-IPv4 VR(ENARSI) Address-Family Neighbors for AS(100)
...
  IP-EIGRP neighbor: 10.14.0.2 (FastEthernet1/1)
    Stub Peer Advertising (CONNECTED SUMMARY) Routes    ! ← stub type confirmed: connected + summary
    Suppressing queries                                  ! ← R1 will NOT query R4 during topology changes
    Hold time is 12, Uptime: 00:03:15
    Version 23.0/2.0, Retrans: 0, Retries: 0
    Prefixes sent: 3   ! ← R4 sends 3 prefixes: 10.14.0.0/30, 10.0.0.4/32, 192.168.4.0/24
```

### Task 3: Stub Reachability and Transit Verification

```
R1# show ip route 192.168.4.0
Routing entry for 192.168.4.0/24
  Known via "eigrp 100", distance 90, metric 130816, type internal
  Redistributing via eigrp 100
  Last update from 10.14.0.2 on FastEthernet1/1, 00:03:30 ago
  Routing Descriptor Blocks:
  * 10.14.0.2, from 10.14.0.2, 00:03:30 ago, via FastEthernet1/1   ! ← via R4 directly
      Route metric is 130816, Traffic Share count is 1

R2# show ip route 192.168.4.0
D    192.168.4.0/24 [90/412416] via 10.12.0.1, 00:03:28, FastEthernet0/0   ! ← via R1 (not R4)

R3# show ip route 192.168.4.0
D    192.168.4.0/24 [90/412416] via 10.13.0.1, 00:03:28, FastEthernet0/0   ! ← via R1 (not R4)

R2# ping 192.168.4.1 source loopback 0
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 192.168.4.1, timeout is 2 seconds:
!!!!!                                                                        ! ← all 5 success
Success rate is 100 percent (5/5)

R1# show ip eigrp topology all-links | section 192.168.4
P 192.168.4.0/24, 1 successors, FD is 130816
        via 10.14.0.2 (130816/28160), FastEthernet1/1   ! ← R4 as only path; not a transit
```

---

## 7. Verification Cheatsheet

### EIGRP Stub Configuration (Named Mode)

```
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  eigrp stub connected summary
 exit-address-family
 address-family ipv6 unicast autonomous-system 100
  eigrp stub connected summary
 exit-address-family
```

| Command | Purpose |
|---------|---------|
| `eigrp stub connected summary` | Advertise connected and summary routes only; suppress queries |
| `eigrp stub receive-only` | Receive routes but advertise nothing (mutually exclusive with other keywords) |
| `eigrp stub leak-map MAP_NAME` | Advertise specific routes permitted by a named route-map |
| `no eigrp stub` | Remove stub status; router becomes a full EIGRP participant |

> **Exam tip:** `eigrp stub receive-only` cannot be combined with any other keyword. Attempting `eigrp stub connected receive-only` will result in an IOS error.

### Activating a New Interface in EIGRP (Named Mode)

```
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  network <subnet> <wildcard>
 exit-address-family
```

| Command | Purpose |
|---------|---------|
| `network 10.14.0.0 0.0.0.3` | Include the 10.14.0.0/30 subnet in EIGRP |
| `network 10.0.0.4 0.0.0.0` | Include exactly one host address (loopback) |
| `network 192.168.4.0 0.0.0.255` | Include the /24 stub LAN |

### Verification Commands

| Command | What to Look For |
|---------|-----------------|
| `show ip eigrp neighbors` | R4 listed as neighbor on R1's Fa1/1; R4 shows R1 as its only neighbor |
| `show ip eigrp neighbors detail` | `Stub Peer Advertising (CONNECTED SUMMARY) Routes` and `Suppressing queries` for R4 |
| `show ip route eigrp` | 192.168.4.0/24 present on R1, R2, R3; R4's routing table includes all domain routes |
| `show ip eigrp topology all-links` | R4 appears as stub peer; 192.168.4.0/24 has a single successor via R4 |
| `show ip eigrp topology 192.168.4.0 255.255.255.0` | Single entry for the stub LAN, via 10.14.0.2 |
| `show ip eigrp interfaces` | Confirms which interfaces are participating in EIGRP |
| `show ip eigrp traffic` | Shows Hello, Update, Query, Reply packet counts — queries to R4 should be zero after stub |

### Wildcard Mask Quick Reference

| Subnet Mask | Wildcard | Common Use |
|-------------|----------|------------|
| /32 (255.255.255.255) | 0.0.0.0 | Host route (loopback) |
| /30 (255.255.255.252) | 0.0.0.3 | Point-to-point link |
| /24 (255.255.255.0) | 0.0.0.255 | LAN or stub network |
| /23 (255.255.254.0) | 0.0.1.255 | Summary covering two /24s |

### Common EIGRP Stub Failure Causes

| Symptom | Likely Cause |
|---------|-------------|
| R4 has no EIGRP neighbors | Passive interface on R4 fa0/0, AS number mismatch, or R1 missing network statement for 10.14.0.0/30 |
| 192.168.4.0/24 absent from R1 routing table | Missing `network 192.168.4.0 0.0.0.255` on R4, or `eigrp stub receive-only` configured |
| R4 not shown as stub on R1 | `eigrp stub` not configured under the address-family on R4 |
| R4 receives no EIGRP routes | R4 incorrectly configured with wrong AS number |
| R2/R3 cannot reach 192.168.4.0/24 | R1 not redistributing R4's routes (check R1 routing table first) |

---

## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these steps first!

### Task 1: Add R4 to the EIGRP Domain

<details>
<summary>Click to view R4 Configuration</summary>

```bash
! R4 — Enable Named Mode EIGRP with AS 100
router eigrp ENARSI
 !
 address-family ipv4 unicast autonomous-system 100
  eigrp log-neighbor-changes
  network 10.14.0.0 0.0.0.3
  network 10.0.0.4 0.0.0.0
  network 192.168.4.0 0.0.0.255
  eigrp router-id 10.0.0.4
  no auto-summary
 exit-address-family
 !
 address-family ipv6 unicast autonomous-system 100
  eigrp log-neighbor-changes
  eigrp router-id 10.0.0.4
 exit-address-family
```

</details>

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1 — Add network statement to include fa1/1 (R4-facing link) in EIGRP
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  network 10.14.0.0 0.0.0.3
 exit-address-family
```

</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
show ip eigrp neighbors           ! R1 must show 3 neighbors; R4 must show 1
show ip route eigrp               ! R4 should have routes to all domain prefixes
show ip eigrp interfaces          ! Fa1/1 must appear on R1; Fa0/0 must appear on R4
```

</details>

---

### Task 2: Configure R4 as an EIGRP Stub Router

<details>
<summary>Click to view R4 Configuration</summary>

```bash
! R4 — Add eigrp stub to both address families
router eigrp ENARSI
 !
 address-family ipv4 unicast autonomous-system 100
  eigrp stub connected summary
 exit-address-family
 !
 address-family ipv6 unicast autonomous-system 100
  eigrp stub connected summary
 exit-address-family
```

</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
show ip eigrp neighbors detail    ! Look for "Stub Peer Advertising (CONNECTED SUMMARY) Routes"
                                  ! and "Suppressing queries" on R1 for neighbor 10.14.0.2
```

</details>

---

### Task 3: Verify Stub Router Behavior

<details>
<summary>Click to view Verification Commands</summary>

```bash
! On R1, R2, R3 — confirm R4's stub LAN is reachable
show ip route 192.168.4.0

! On R2 — confirm R4 is not in the transit path to R3
traceroute 10.0.0.3 source loopback 0   ! must go R2→R1→R3, never through R4

! On R1 — confirm R4 appears as stub peer in topology
show ip eigrp topology all-links

! End-to-end reachability test
ping 192.168.4.1 source loopback 0      ! from R2 and R3
```

</details>

---

## 9. Troubleshooting Scenarios

Each ticket simulates a real-world fault. Inject the fault first, then diagnose and fix using only `show` commands.

### Workflow

```bash
python3 setup_lab.py                                   # reset to known-good state
python3 scripts/fault-injection/inject_scenario_01.py  # Ticket 1
python3 scripts/fault-injection/inject_scenario_02.py  # Ticket 2
python3 scripts/fault-injection/inject_scenario_03.py  # Ticket 3
python3 scripts/fault-injection/apply_solution.py      # restore all faults
```

---

### Ticket 1 — R4 Drops Off the EIGRP Neighbor Table on R1

A network operations alert fires: R4 has stopped participating in EIGRP. R1's neighbor table no longer lists R4, and 192.168.4.0/24 has disappeared from all routing tables. No physical changes were made to the cabling.

**Inject:** `python3 scripts/fault-injection/inject_scenario_01.py`

**Success criteria:** `show ip eigrp neighbors` on R1 shows R4 at 10.14.0.2 on Fa1/1, and `show ip route 192.168.4.0` returns a valid EIGRP route on R1, R2, and R3.

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Step 1: Confirm R4 is missing from R1's neighbor table
R1# show ip eigrp neighbors
! Expected: only R2 and R3 appear

! Step 2: Check if R4's interface is up
R4# show interfaces FastEthernet0/0
! Expected: line protocol is up — the physical link is fine

! Step 3: Verify EIGRP is running on R4
R4# show ip eigrp interfaces
! Expected: Fa0/0 should NOT appear — it has been made passive

! Step 4: Check passive-interface status
R4# show ip protocols
! Look for "Passive Interface(s):" section
! Expected: FastEthernet0/0 listed as passive — Hellos suppressed on this interface

! Step 5: Check R4's address-family configuration
R4# show running-config | section router eigrp
! Look for "af-interface FastEthernet0/0" with "passive-interface" under it
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! R4 — Remove passive-interface from fa0/0 within the address-family
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  af-interface FastEthernet0/0
   no passive-interface
  exit-af-interface
 exit-address-family

! Verify adjacency re-forms (may take up to 30 seconds)
R1# show ip eigrp neighbors
! Expected: R4 at 10.14.0.2 on Fa1/1 reappears
```

</details>

---

### Ticket 2 — R4's Networks Have Vanished While the Link Stays Up

The helpdesk reports that workstations at the satellite office (192.168.4.0/24) are unreachable from headquarters and all branch offices. However, a ping from R1 to R4's interface address (10.14.0.2) succeeds, confirming the physical link is operational.

**Inject:** `python3 scripts/fault-injection/inject_scenario_02.py`

**Success criteria:** `show ip route 192.168.4.0` returns a valid EIGRP route on R1, R2, and R3. `show ip eigrp neighbors detail` on R1 shows R4 with `Stub Peer Advertising (CONNECTED SUMMARY) Routes`.

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Step 1: Confirm 192.168.4.0/24 is missing from R1's routing table
R1# show ip route 192.168.4.0
! Expected: % Network not in table (or similar)

! Step 2: Confirm R4 is still in the neighbor table (link-level is fine)
R1# show ip eigrp neighbors
! Expected: R4 at 10.14.0.2 still present

! Step 3: Confirm R4 is advertising nothing
R1# show ip eigrp topology all-links | include 192.168
! Expected: no output — 192.168.4.0/24 not in topology table

! Step 4: Check what stub type R4 is advertising
R1# show ip eigrp neighbors detail
! Look for "Stub Peer Advertising" line for 10.14.0.2
! Expected: "Stub Peer Advertising ( ) Routes" (receive-only shows blank brackets)
! or "Stub Peer Advertising (RECEIVE-ONLY) Routes"

! Step 5: Confirm by checking R4's running config
R4# show running-config | section router eigrp
! Look for "eigrp stub receive-only" — this prevents R4 from advertising anything
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! R4 — Change stub type from receive-only back to connected + summary
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  eigrp stub connected summary
 exit-address-family
 address-family ipv6 unicast autonomous-system 100
  eigrp stub connected summary
 exit-address-family

! Verify
R1# show ip eigrp neighbors detail
! Expected: "Stub Peer Advertising (CONNECTED SUMMARY) Routes"
R1# show ip route 192.168.4.0
! Expected: D    192.168.4.0/24 via 10.14.0.2
```

</details>

---

### Ticket 3 — The Satellite Office LAN Is Gone but R4 Shows a Healthy Adjacency

An operator reports that 192.168.4.0/24 has disappeared from R1's routing table. Strangely, `show ip eigrp neighbors` on R1 still lists R4 with a normal uptime — no adjacency flap has been logged. The stub flag is also intact.

**Inject:** `python3 scripts/fault-injection/inject_scenario_03.py`

**Success criteria:** `show ip route 192.168.4.0` returns an EIGRP route on R1, R2, and R3. `show ip eigrp interfaces` on R4 lists Lo1 (or the network statement for 192.168.4.0/24 is present).

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Step 1: Verify the route is missing
R1# show ip route 192.168.4.0
! Expected: % Network not in table

! Step 2: Confirm adjacency is fine (adjacency is NOT the issue)
R1# show ip eigrp neighbors
! Expected: R4 at 10.14.0.2 present, normal hold time

! Step 3: Check what prefixes R4 is actually advertising
R1# show ip eigrp topology all-links | begin 192
! Expected: 192.168.4.0/24 missing from the topology table

! Step 4: On R4, verify which prefixes it is advertising
R4# show ip eigrp topology
! Check if 192.168.4.0/24 appears — it won't if network stmt is absent

! Step 5: Check R4's EIGRP network statements
R4# show running-config | section router eigrp
! Expected: missing "network 192.168.4.0 0.0.0.255" under the IPv4 address-family

! Step 6: Confirm Lo1 has the correct IP
R4# show interfaces Loopback1
! Expected: 192.168.4.1/24 — interface is up but not in EIGRP
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! R4 — Re-add the missing network statement for the stub LAN
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  network 192.168.4.0 0.0.0.255
 exit-address-family

! Verify
R4# show ip eigrp topology
! Expected: 192.168.4.0/24 appears as a connected route

R1# show ip route 192.168.4.0
! Expected: D    192.168.4.0/24 [90/...] via 10.14.0.2
```

</details>

---

## 10. Lab Completion Checklist

### Core Implementation

- [ ] R4 enters the EIGRP domain — `show ip eigrp neighbors` on R1 shows three neighbors (R2, R3, R4)
- [ ] R4 has exactly one EIGRP neighbor: R1 at 10.14.0.1
- [ ] R4's stub LAN (192.168.4.0/24) is reachable from R1, R2, and R3 via EIGRP
- [ ] `show ip eigrp neighbors detail` on R1 shows `Stub Peer Advertising (CONNECTED SUMMARY) Routes` for R4
- [ ] `show ip eigrp neighbors detail` on R1 shows `Suppressing queries` for R4
- [ ] R2 and R3 do NOT show stub flags — only R4 is a stub
- [ ] `ping 192.168.4.1 source loopback 0` from R2 succeeds (5/5)
- [ ] `ping 192.168.4.1 source loopback 0` from R3 succeeds (5/5)
- [ ] R4's routing table includes EIGRP routes for 10.0.0.1/32, 10.0.0.2/32, 10.0.0.3/32, 172.16.20.0/23, 172.16.30.0/23

### Troubleshooting

- [ ] Ticket 1: Diagnosed passive-interface fault on R4 fa0/0; restored adjacency
- [ ] Ticket 2: Identified `eigrp stub receive-only` misconfiguration; corrected to `connected summary`
- [ ] Ticket 3: Found missing network statement for 192.168.4.0/24 on R4; restored route advertisement
- [ ] `python3 scripts/fault-injection/apply_solution.py` restores all three faults cleanly
