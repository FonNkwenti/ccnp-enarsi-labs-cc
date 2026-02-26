# Lab 04: Loop-Free Path Selection — FD, RD, FC & Feasible Successors

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

**Exam Objective:** 1.9.c — Loop-free path selection (RD, FD, FC, successor, feasible successor); 1.9.e — Load balancing (equal-cost, unequal-cost)

EIGRP's loop prevention is not merely a policy—it is a mathematical guarantee enforced by the Diffusing Update Algorithm (DUAL). Where other protocols rely on periodic reconvergence cycles or time-based loop detection, EIGRP pre-computes backup routes whose correctness is proven before a link failure occurs. This lab explores the precise mechanics of that guarantee: Feasible Distance, Reported Distance, the Feasibility Condition, and the variance multiplier that enables traffic to flow across multiple unequal paths simultaneously.

### The EIGRP Topology Table and DUAL

Every EIGRP router maintains a topology table separate from the routing table. The topology table contains every prefix learned from every neighbor, along with the composite metric each neighbor reported and the router's own calculated metric to reach that prefix.

Key terminology:

| Term | Abbreviation | Definition |
|------|------|-----------|
| Feasible Distance | FD | The best composite metric this router has ever computed to reach a prefix (the "best known metric") |
| Reported Distance | RD | The composite metric the advertising neighbor claims for the same prefix (what they reported) |
| Successor | — | The neighbor providing the current best path; its route is installed in the routing table |
| Feasible Successor | FS | A neighbor whose RD is less than the local FD — a mathematically loop-free backup |
| Active State | — | A route with no FS enters ACTIVE when the successor fails; DUAL sends queries to all neighbors |
| Passive State | — | Normal steady-state; both successor and (optionally) feasible successor routes are in PASSIVE |

The routing table only shows the Successor route. The topology table (`show ip eigrp topology`) exposes every path, including feasible successors and the RD/FD values that determine whether the Feasibility Condition is satisfied.

### Feasibility Condition and Loop-Free Guarantee

The Feasibility Condition (FC) is a single inequality:

```
FC is met when: RD_neighbor < FD_local
```

Where:
- `RD_neighbor` = the metric the neighbor claims for the destination
- `FD_local` = the router's own best-known metric (Feasible Distance) to the same destination

If a neighbor's RD is strictly less than the local FD, that neighbor cannot be routing traffic through this router to reach the destination. Why? Because if it were, the neighbor's own metric would be at least as large as the local FD—not smaller. The mathematical inequality is proof of loop freedom.

**Critical nuance:** The FC uses the historical FD (the best metric ever seen), not the current metric. This prevents situations where a degraded successor briefly satisfies the condition during a failure event.

**When FC fails:** If no neighbor satisfies the FC, EIGRP sends QUERY messages to all neighbors. The route enters ACTIVE state. Reconvergence time depends on query propagation; stub routers (Lab 06) limit this scope.

### Composite Metric Formula (Default K-Values)

With default K-values (K1=1, K2=0, K3=1, K4=0, K5=0):

```
Metric = (10^7 / BW_min  +  delay_sum)  ×  256
```

Where `BW_min` = minimum bandwidth (kbps) along the entire path, and `delay_sum` = sum of all interface delays (in tens of microseconds) along the path.

Reference values for this lab's topology:

| Interface | Bandwidth (kbps) | Delay (×10 µs) | Notes |
|-----------|-----------------|-----------------|-------|
| FastEthernet (default) | 100,000 | 100 | R1 fa1/0, R2 fa0/0, fa0/1, R3 fa0/0, fa0/1 |
| R1 fa0/0 | **512** | **2000** | Degraded from Lab 03 metric-tuning exercise |
| Loopback0 | 8,000 | 5,000 | All routers |

### Unequal-Cost Load Balancing with Variance

By default EIGRP installs only the successor route (equal-cost load balancing requires identical metrics). The `variance` multiplier allows EIGRP to install additional paths from the topology table into the routing table, provided:

1. **The path is a Feasible Successor** (FC must be met — this is non-negotiable)
2. **The path's FD ≤ variance × successor_FD**

```
Unequal-cost path is installed when:
  FD_candidate  ≤  variance  ×  FD_successor
  AND FC is met (RD_candidate < FD_successor)
```

Traffic is distributed in inverse proportion to the composite metric: the better path carries proportionally more packets.

**Skills this lab develops:**

| Skill | Description |
|-------|-------------|
| Topology table analysis | Interpret `show ip eigrp topology` to read FD, RD, and path state |
| Feasibility Condition evaluation | Determine whether a given alternate path qualifies as a Feasible Successor |
| Instant failover verification | Observe DUAL promoting a FS to successor without sending QUERY messages |
| Variance configuration | Calculate the required variance multiplier and verify UCAL in the routing table |
| ACTIVE vs PASSIVE diagnosis | Identify routes stuck in ACTIVE state due to missing FS |

---

## 2. Topology & Scenario

As the lead network engineer at Acme Corp, you are auditing the EIGRP WAN core following last week's lab exercise, which left R1's direct link to Branch A (R2) intentionally degraded for metric experimentation. Your task is to formally document the loop-free path selection state of the network, validate the Feasibility Condition for all alternate paths, verify automatic failover behaviour, and configure unequal-cost load balancing so the degraded R1–R2 link carries a proportional share of traffic rather than sitting idle.

```
              ┌──────────────────────────────┐
              │             R1               │
              │        (Hub / Core)          │
              │    Lo0: 10.0.0.1/32          │
              └──────┬───────────────┬───────┘
         Fa0/0 [DEG] │               │ Fa1/0
       10.12.0.1/30  │               │ 10.13.0.1/30
                     │               │
       10.12.0.2/30  │               │ 10.13.0.2/30
               Fa0/0 │               │ Fa0/0
     ┌────────────────┘               └────────────────┐
     │                                                 │
┌────┴──────────────────┐         ┌────────────────────┴────┐
│          R2            │         │           R3            │
│      (Branch A)        │         │       (Branch B)        │
│   Lo0: 10.0.0.2/32    │         │   Lo0: 10.0.0.3/32     │
└──────────┬─────────────┘         └──────────┬──────────────┘
       Fa0/1│                                 │Fa0/1
  10.23.0.1/30                          10.23.0.2/30
            └─────────────────────────────────┘
                         10.23.0.0/30

[DEG] = R1 fa0/0 degraded: bandwidth 512 kbps, delay 2000 (×10 µs) — inherited from Lab 03
```

**Address Summary:**

| Subnet | Link | Devices |
|--------|------|---------|
| 10.12.0.0/30 | R1 fa0/0 — R2 fa0/0 | Hub ↔ Branch A (degraded) |
| 10.13.0.0/30 | R1 fa1/0 — R3 fa0/0 | Hub ↔ Branch B |
| 10.23.0.0/30 | R2 fa0/1 — R3 fa0/1 | Branch A ↔ Branch B (alternate path) |
| 10.0.0.1/32 | R1 Lo0 | Hub loopback (router-ID) |
| 10.0.0.2/32 | R2 Lo0 | Branch A loopback (router-ID) |
| 10.0.0.3/32 | R3 Lo0 | Branch B loopback (router-ID) |

---

## 3. Hardware & Environment Specifications

**Platform:** GNS3 on Apple Silicon — Dynamips c7200, IOS 15.3(3)XB12

**Adapter Cards:**

| Router | Slot | Card | Interfaces |
|--------|------|------|-----------|
| R1 | 0 | C7200-IO-FE | fa0/0 |
| R1 | 1 | PA-2FE-TX | fa1/0, fa1/1 |
| R2 | 0 | C7200-IO-2FE | fa0/0, fa0/1 |
| R3 | 0 | C7200-IO-2FE | fa0/0, fa0/1 |

**Cabling Table:**

| Link ID | Source | Source Interface | Target | Target Interface | Subnet |
|---------|--------|-----------------|--------|-----------------|--------|
| L1 | R1 | fa0/0 | R2 | fa0/0 | 10.12.0.0/30 |
| L2 | R1 | fa1/0 | R3 | fa0/0 | 10.13.0.0/30 |
| L3 | R2 | fa0/1 | R3 | fa0/1 | 10.23.0.0/30 |

**Console Access Table:**

| Device | Console Port | Connection Command |
|--------|-------------|-------------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |

---

## 4. Base Configuration

The following is pre-loaded via `setup_lab.py` (initial-configs from Lab 03 solutions):

**Pre-configured on all routers:**
- Hostnames, `no ip domain-lookup`, `ipv6 unicast-routing`
- Loopback0 IPv4 and IPv6 addresses
- FastEthernet interface IPv4 and IPv6 addresses, `no shutdown`
- EIGRP Named Mode (`router eigrp ENARSI`) with:
  - IPv4 address-family AS 100 — network statements, `eigrp router-id`, `no auto-summary`, `eigrp log-neighbor-changes`
  - IPv6 address-family AS 100 — `eigrp router-id`, `eigrp log-neighbor-changes`
- **R1 fa0/0:** `bandwidth 512` and `delay 2000` carried forward from Lab 03

**NOT pre-configured (student must add):**
- Variance for unequal-cost load balancing
- Any metric adjustments beyond what Lab 03 established

---

## 5. Lab Challenge: Core Implementation

### Task 1: Analyze the EIGRP Topology Table

- On each router, examine the full EIGRP IPv4 topology table for all known prefixes.
- For every prefix, record: the Feasible Distance, the Reported Distance from each advertising neighbor, the current Successor, and whether any Feasible Successor exists.
- Pay particular attention to R1's routes to 10.0.0.2/32 and 10.0.0.3/32 — these two prefixes demonstrate the difference between a route that does and does not qualify for a Feasible Successor due to the degraded R1–R2 link.

**Verification:** `show ip eigrp topology` on each router must display at least one prefix with both a Successor and a Feasible Successor path. Record the FD and RD values — you will need them for Task 2.

---

### Task 2: Verify the Feasibility Condition

- For R1's route to 10.0.0.2/32, extract the RD advertised by R2 (the direct path) and compare it to R1's current FD via R3 (the successor path).
- State explicitly whether the Feasibility Condition is met (RD < FD) for R2 as a potential Feasible Successor.
- For R1's route to 10.0.0.3/32, perform the same check for the path via R2. Explain why this path does or does not qualify as a Feasible Successor.
- Use `show ip eigrp topology [prefix] [mask]` for precise per-prefix detail rather than the full table.

**Verification:** `show ip eigrp topology 10.0.0.2 255.255.255.255` on R1 must show the path via R2 tagged as a Feasible Successor (FS). `show ip eigrp topology 10.0.0.3 255.255.255.255` on R1 must show no Feasible Successor.

---

### Task 3: Simulate Successor Failure and Verify Instant Failover

- On R1, administratively shut R1's interface toward Branch B (fa1/0) to simulate a link failure. This forces R1 to rely on its Feasible Successor for 10.0.0.2/32.
- Immediately check R1's routing table for 10.0.0.2/32. Verify the route is still present and now routes via the Feasible Successor without entering ACTIVE state.
- Also verify that R1's route to 10.0.0.3/32 (which has no FS) enters ACTIVE and requires query/reply reconvergence before returning.
- Restore fa1/0 (no shutdown) and confirm both routes return to their pre-failure state.

**Verification:** Immediately after shutdown, `show ip route 10.0.0.2` on R1 must show the route via R2 fa0/0 (Feasible Successor promoted). `show ip eigrp topology active` should show 10.0.0.3 in ACTIVE state but NOT 10.0.0.2.

---

### Task 4: Configure Unequal-Cost Load Balancing with Variance

- Calculate the minimum variance multiplier required for R1 to install both paths to 10.0.0.2/32 in its routing table (successor via R3 and the Feasible Successor via R2 direct).
  - FD_successor (via R3) = 1,651,200
  - FD_feasible_successor (via R2 direct) = 6,791,936
  - Required variance = ceiling(6,791,936 / 1,651,200) + 1 = 5
- On R1, under the EIGRP IPv4 address-family, set variance to 5.
- Verify the routing table shows two paths to 10.0.0.2/32 with different metrics.
- Observe the traffic-share ratio — R3's path should carry approximately 4× the traffic of the direct R2 path.

**Verification:** `show ip route 10.0.0.2` on R1 must show two EIGRP entries — one via R3 fa1/0 and one via R2 fa0/0. `show ip eigrp topology 10.0.0.2 255.255.255.255` must confirm both paths are in PASSIVE state.

---

## 6. Verification & Analysis

### Task 1: Topology Table — R1

```
R1# show ip eigrp topology
EIGRP-IPv4 VR(ENARSI) Topology Table for AS(100)/ID(10.0.0.1)
Codes: P - Passive, A - Active, U - Update, Q - Query, R - Reply,
       r - reply Status, s - stub Status

P 10.0.0.2/32, 1 successors, FD is 1651200            ! ← FD via R3 (successor)
        via 10.13.0.2 (1651200/1625600), FastEthernet1/0  ! ← R3 RD=1,625,600 (successor)
        via 10.12.0.2 (6791936/1600000), FastEthernet0/0  ! ← R2 RD=1,600,000 (FS — FC met)

P 10.0.0.3/32, 1 successors, FD is 1625600            ! ← FD via R3
        via 10.13.0.2 (1625600/1600000), FastEthernet1/0  ! ← Successor; no FS listed

P 10.12.0.0/30, 1 successors, FD is 5511936           ! ← Directly connected via fa0/0
        via Connected, FastEthernet0/0

P 10.13.0.0/30, 1 successors, FD is 51200             ! ← Directly connected via fa1/0
        via Connected, FastEthernet1/0

P 10.23.0.0/30, 1 successors, FD is 307200            ! ← R2 reports 256000, R3 reports 256000
        via 10.13.0.2 (307200/256000), FastEthernet1/0
        via 10.12.0.2 (6817536/256000), FastEthernet0/0
```

### Task 2: Feasibility Condition Check — R1 to 10.0.0.2/32

```
R1# show ip eigrp topology 10.0.0.2 255.255.255.255
EIGRP-IPv4 VR(ENARSI) Topology Entry for AS(100)/ID(10.0.0.1) for 10.0.0.2/32
  State is Passive, Query origin flag is 1, 1 Successor(s), FD is 1651200
  Descriptor Blocks:
  10.13.0.2 (FastEthernet1/0), from 10.13.0.2, Send flag is 0x0
      Composite metric is (1651200/1625600), route is Successor      ! ← FD=1,651,200 | RD=1,625,600
      Vector metric:
        Minimum bandwidth is 8000 Kbit
        Total delay is 5200 microseconds
  10.12.0.2 (FastEthernet0/0), from 10.12.0.2, Send flag is 0x0
      Composite metric is (6791936/1600000), route is Feasible Successor  ! ← FS: RD=1,600,000 < FD=1,651,200 ✓
      Vector metric:
        Minimum bandwidth is 512 Kbit
        Total delay is 7000 microseconds

! FC ANALYSIS:
! R2's RD = 1,600,000
! R1's FD (successor) = 1,651,200
! 1,600,000 < 1,651,200 → FC is MET → R2 qualifies as Feasible Successor ✓
```

```
R1# show ip eigrp topology 10.0.0.3 255.255.255.255
EIGRP-IPv4 VR(ENARSI) Topology Entry for AS(100)/ID(10.0.0.1) for 10.0.0.3/32
  State is Passive, Query origin flag is 1, 1 Successor(s), FD is 1625600
  Descriptor Blocks:
  10.13.0.2 (FastEthernet1/0), from 10.13.0.2, Send flag is 0x0
      Composite metric is (1625600/1600000), route is Successor      ! ← FD=1,625,600 | RD=1,600,000
  10.12.0.2 (FastEthernet0/0), from 10.12.0.2, Send flag is 0x0
      Composite metric is (6817536/1625600), route is not a Feasible Successor  ! ← R2 RD=1,625,600
      Feasibility condition not met for this peer
! FC ANALYSIS:
! R2's RD for 10.0.0.3 = 1,625,600
! R1's FD (successor) = 1,625,600
! 1,625,600 < 1,625,600? NO — equal is not less → FC FAILS → no FS for 10.0.0.3 ✗
```

### Task 3: Instant Failover Verification

```
R1# shutdown (on fa1/0)
R1# show ip route 10.0.0.2
Routing entry for 10.0.0.2/32
  Known via "eigrp 100", distance 90, metric 6791936
  Redistributing via eigrp 100
  Last update from 10.12.0.2 on FastEthernet0/0
    * 10.12.0.2, from 10.12.0.2, 00:00:03 ago, via FastEthernet0/0  ! ← Promoted from FS instantly

R1# show ip eigrp topology active
EIGRP-IPv4 VR(ENARSI) Topology Table for AS(100)/ID(10.0.0.1)
A 10.0.0.3/32, 0 successors, FD is 1625600, Q-count 2   ! ← 10.0.0.3 ACTIVE (no FS, querying)
! NOTE: 10.0.0.2 does NOT appear here — it converged instantly via FS ✓
```

### Task 4: Unequal-Cost Load Balancing (After variance 5)

```
R1# show ip route 10.0.0.2
Routing entry for 10.0.0.2/32
  Known via "eigrp 100", distance 90, metric 1651200
  Redistributing via eigrp 100
  Last update from 10.13.0.2 on FastEthernet1/0
    * 10.13.0.2, from 10.13.0.2, via FastEthernet1/0, metric 1651200  ! ← Successor (4 shares)
    * 10.12.0.2, from 10.12.0.2, via FastEthernet0/0, metric 6791936  ! ← FS UCAL (1 share)

R1# show ip eigrp topology 10.0.0.2 255.255.255.255
  Descriptor Blocks:
  10.13.0.2 (FastEthernet1/0): Composite metric (1651200/1625600), route is Successor  ! ← P state ✓
  10.12.0.2 (FastEthernet0/0): Composite metric (6791936/1600000), route is Feasible Successor  ! ← P state ✓
! Both paths PASSIVE — no ACTIVE state, no queries sent ✓
! Traffic share ratio ≈ 4:1 (R3 path carries ~4× more packets)
```

---

## 7. Verification Cheatsheet

### EIGRP Topology Table Commands

```
show ip eigrp topology
show ip eigrp topology [prefix] [mask]
show ip eigrp topology all-links
show ip eigrp topology active
```

| Command | What to Look For |
|---------|-----------------|
| `show ip eigrp topology` | All Passive routes; FD for each; Successor and FS per prefix |
| `show ip eigrp topology [prefix] [mask]` | Per-route detail: exact FD/RD values, Feasibility Condition pass/fail annotation |
| `show ip eigrp topology all-links` | Shows EVERY known path, including those that failed FC (not just FS) |
| `show ip eigrp topology active` | Lists any routes in ACTIVE state (sending queries); should be empty in steady state |

### Feasibility Condition Evaluation

```
! Read from: show ip eigrp topology [prefix] [mask]
! Composite metric is (LOCAL_FD / NEIGHBOR_RD)
!                                ↑ second number = RD
! FC passes when: RD < FD_of_current_Successor
! FC fails when:  RD >= FD_of_current_Successor  → "not a Feasible Successor"
```

| Check | Command | Expected |
|-------|---------|---------|
| Successor metric | `show ip eigrp topology [prefix]` | First entry shows "route is Successor" |
| Feasible Successor | `show ip eigrp topology [prefix]` | Second entry shows "route is Feasible Successor" |
| No FS | `show ip eigrp topology [prefix]` | "Feasibility condition not met" on alternate entry |

### Variance Configuration

```
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  variance [multiplier]
  maximum-paths [1-32]
 exit-address-family
```

| Command | Purpose |
|---------|---------|
| `variance N` | Install paths with FD ≤ N × FD_successor AND FC met |
| `maximum-paths N` | Limit number of load-balanced paths (default 4) |
| `traffic-share balanced` | Default: distribute traffic proportional to inverse metric |
| `traffic-share min` | Send all traffic via best path only (ignores variance for forwarding) |

> **Exam tip:** Variance only installs paths that are already Feasible Successors. If the Feasibility Condition is not met, no variance value will install that path — it is a hard requirement, not overrideable.

### Verification Commands

| Command | What to Look For |
|---------|-----------------|
| `show ip eigrp topology` | Successor + FS entries; all routes in P (Passive) state |
| `show ip eigrp topology all-links` | Paths that failed FC (not labeled FS despite being known) |
| `show ip route eigrp` | UCAL: two `D` entries for same prefix with different metrics and next-hops |
| `show ip eigrp topology active` | Should show nothing in steady state; entries here mean DUAL is querying |
| `show ip eigrp neighbors` | Adjacencies must be UP before topology table is valid |

### Wildcard Mask Quick Reference

| Subnet Mask | Wildcard Mask | Common Use |
|-------------|---------------|-----------|
| /30 (255.255.255.252) | 0.0.0.3 | Point-to-point WAN links |
| /32 (255.255.255.255) | 0.0.0.0 | Loopback interfaces |
| /24 (255.255.255.0) | 0.0.255.255 | LAN segments |

### Common EIGRP Path-Selection Failure Causes

| Symptom | Likely Cause |
|---------|-------------|
| No Feasible Successor in topology table | RD ≥ FD of successor — FC not met; need metric adjustment |
| UCAL paths not in routing table despite variance | FS is not a Feasible Successor — variance is irrelevant without FC |
| Route stuck in ACTIVE state | No FS; DUAL sent queries that were not replied to (SIA) |
| Routing table shows only one path after variance set | variance value too low: FD_alternate > variance × FD_best |
| Convergence after fa0/0 shutdown takes seconds | That path had no FS — DUAL had to query neighbors |

---

## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these steps first!

### Task 1–3: Observation and Failover Testing

<details>
<summary>Click to view Analysis Notes</summary>

Tasks 1–3 require no persistent configuration changes. The topology table analysis and failover test are read-only exercises (shutdown/no shutdown is transient). The FD and RD values to record are:

| Router | Prefix | Successor Via | FD | FS Via | RD (FS) | FC? |
|--------|--------|--------------|-----|--------|---------|-----|
| R1 | 10.0.0.2/32 | R3 fa1/0 | 1,651,200 | R2 fa0/0 | 1,600,000 | YES |
| R1 | 10.0.0.3/32 | R3 fa1/0 | 1,625,600 | — | 1,625,600 | NO |

</details>

### Task 4: Variance for Unequal-Cost Load Balancing

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1 — Add variance 5 under IPv4 address-family only
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  variance 5
 exit-address-family
```

</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
show ip route 10.0.0.2
! Expect: two EIGRP entries (via 10.13.0.2 and via 10.12.0.2)

show ip eigrp topology 10.0.0.2 255.255.255.255
! Expect: both paths in Passive state; R2 path still labeled Feasible Successor
```

</details>

---

## 9. Troubleshooting Scenarios

Each ticket simulates a real-world fault. Inject the fault first, then diagnose and fix using only show commands and targeted configuration changes.

### Workflow

```bash
python3 setup_lab.py                                   # reset to known-good
python3 scripts/fault-injection/inject_scenario_01.py  # Ticket 1
python3 scripts/fault-injection/apply_solution.py      # restore
```

---

### Ticket 1 — R1 Reports No Backup Path for Branch A Networks

The overnight monitoring system has flagged that R1 will not converge instantly to Branch A should the R1–R3 link fail. The NOC notes that the EIGRP topology table "looks different from yesterday."

**Inject:** `python3 scripts/fault-injection/inject_scenario_01.py`

**Success criteria:** R1's topology table shows a Feasible Successor for 10.0.0.2/32 and convergence to Branch A does not require DUAL queries.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. `show ip eigrp topology 10.0.0.2 255.255.255.255` on R1 — look for "Feasibility condition not met" on the via-R2 path
2. Note the RD value R2 is now advertising for 10.0.0.2. Compare it to R1's current FD via R3.
3. If RD ≥ FD, FC is broken. The RD change came from R2's own metric to 10.0.0.2 increasing.
4. On R2, `show interface Loopback0` — check the delay value. An elevated delay increases R2's metric to its own loopback, raising the RD it advertises to R1.
5. Compare against baseline: default Lo0 delay = 5000 (×10 µs).

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R2:
interface Loopback0
 no delay
! Restores default delay (5000), bringing R2's RD back to 1,600,000
! FC: 1,600,000 < 1,651,200 → FS restored on R1 for 10.0.0.2/32
```

Verify: `show ip eigrp topology 10.0.0.2 255.255.255.255` on R1 → via-R2 path must show "route is Feasible Successor"

</details>

---

### Ticket 2 — R1 Uses Only One Path to Branch A Despite Load-Balancing Requirement

The capacity-planning team reports that the direct R1–R2 link is carrying zero traffic even though UCAL was configured to share load. Traffic is flowing only via the R1–R3–R2 path.

**Inject:** `python3 scripts/fault-injection/inject_scenario_02.py`

**Success criteria:** Both the R3 and the direct R2 paths appear in R1's routing table for 10.0.0.2/32, with traffic distributed across them.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. `show ip route 10.0.0.2` on R1 — if only one path appears, UCAL is not active.
2. `show ip eigrp topology 10.0.0.2 255.255.255.255` — check whether both paths are in Passive state. If the FS is still present, the issue is the variance value, not the FC.
3. `show running-config | section address-family ipv4` on R1 — check the variance value. If it reads `variance 1` (or is absent), UCAL is disabled.
4. Calculate the required variance: FD_FS / FD_successor = 6,791,936 / 1,651,200 ≈ 4.11 → minimum variance = 5.

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R1:
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  variance 5
 exit-address-family
```

Verify: `show ip route 10.0.0.2` on R1 → two EIGRP entries must appear.

</details>

---

### Ticket 3 — Branch A Route Enters ACTIVE State After a Link Flap

After a brief maintenance window, R1 is experiencing slow convergence to 10.0.0.2/32 whenever the direct R1–R2 link bounces. The NOC observes that the route enters ACTIVE state instead of switching to a backup path instantly.

**Inject:** `python3 scripts/fault-injection/inject_scenario_03.py`

**Success criteria:** R1's Feasible Successor for 10.0.0.2/32 is restored, and a simulated R1 fa0/0 shutdown converges without entering ACTIVE state.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. `show ip eigrp topology 10.0.0.2 255.255.255.255` on R1 — look at both entries. Check which path is now the Successor and which (if any) is the FS.
2. The injected fault changes metric conditions so that R3's path no longer serves as the Successor — and the new Successor's FD has changed, potentially invalidating the FC for what was previously the FS.
3. On R3, `show interface FastEthernet0/1` — check the delay. An elevated delay on R3 fa0/1 increases R3's metric toward R2, which changes the RD R3 reports to R1 for R2's networks.
4. If R3's reported RD ≥ R1's FD via direct path, the via-R3 path fails FC and the FS disappears.
5. Compare against baseline: default fa0/1 delay = 100 (×10 µs).

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R3:
interface FastEthernet0/1
 no delay
! Restores default delay (100), reducing R3's metric toward R2
! R3's RD for R2 networks drops back to 1,625,600
! FC check on R1: 1,625,600 < 1,651,200 (new FD via R3) → FS restored
```

Wait for EIGRP to reconverge (~15 s), then verify:
`show ip eigrp topology 10.0.0.2 255.255.255.255` on R1 → "route is Feasible Successor" must reappear on the via-R3 or via-R2 path as appropriate.

</details>

---

## 10. Lab Completion Checklist

### Core Implementation

- [ ] R1's topology table shows 10.0.0.2/32 with a Feasible Successor via R2 fa0/0
- [ ] R1's topology table shows 10.0.0.3/32 with NO Feasible Successor (FC fails)
- [ ] FC analysis confirmed: R2's RD (1,600,000) < R1's FD via R3 (1,651,200) for 10.0.0.2/32
- [ ] FC analysis confirmed: R2's RD (1,625,600) = R1's FD for 10.0.0.3/32 — not strictly less → no FS
- [ ] Simulated fa1/0 shutdown: 10.0.0.2/32 converged instantly via FS; 10.0.0.3/32 entered ACTIVE
- [ ] fa1/0 restored: both routes returned to pre-failure state
- [ ] `variance 5` configured on R1 IPv4 AF
- [ ] `show ip route 10.0.0.2` shows two EIGRP paths (UCAL active)
- [ ] Traffic-share ratio approximately 4:1 (R3 path vs direct R2 path)
- [ ] All routes remain Passive; no ACTIVE entries in steady state

### Troubleshooting

- [ ] Ticket 1: Identified elevated R2 Lo0 delay breaking FC; restored with `no delay`
- [ ] Ticket 2: Identified variance reset to 1; restored with `variance 5`
- [ ] Ticket 3: Identified elevated R3 fa0/1 delay changing RD; restored with `no delay`
