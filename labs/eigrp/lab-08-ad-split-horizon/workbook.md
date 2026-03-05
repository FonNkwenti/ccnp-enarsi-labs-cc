# Lab 08: Administrative Distance & Split Horizon

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

**Exam Objective:** 1.1 — Troubleshoot administrative distance (all routing protocols); 1.3 — Troubleshoot loop prevention mechanisms (split horizon)

Administrative Distance and split horizon are two foundational mechanisms that determine which routes a router installs in its Routing Information Base (RIB) and how routing information flows through a network. Together they control route preference and prevent the routing loops that would otherwise make distance-vector protocols unstable.

### Administrative Distance

Administrative Distance (AD) is a measure of the trustworthiness of a routing source. When a router learns the same prefix from multiple sources — an EIGRP update, a static route, and an OSPF update — AD determines which one wins a place in the routing table. Lower AD means higher trust.

**Default AD values (IOS reference):**

| Routing Source | Default AD |
|----------------|-----------|
| Connected | 0 |
| Static | 1 |
| EIGRP Summary | 5 |
| eBGP | 20 |
| EIGRP Internal | 90 |
| OSPF | 110 |
| IS-IS | 115 |
| RIP | 120 |
| EIGRP External | 170 |
| iBGP | 200 |
| Unusable | 255 |

**AD = 255** is a special case: a route with AD 255 is never installed in the routing table. This is how you effectively "disable" a routing source for a specific prefix.

**Floating static routes** exploit AD: by configuring a static route with an AD higher than the routing protocol, the static stays dormant as long as the dynamic route is present. If the dynamic route is withdrawn (link failure, adjacency loss), the static "floats" into the RIB as a backup path. This is a common high-availability design pattern.

```
! Default EIGRP at AD 90 wins over this static (AD 91)
ip route 10.0.0.4 255.255.255.255 10.23.0.2 91

! Static at AD 90 — same as EIGRP default. IOS breaks the tie by metric:
! static metric = 0, EIGRP metric = composite value (large) → static wins
ip route 10.0.0.4 255.255.255.255 10.23.0.2 90

! Set EIGRP internal AD to 80 → EIGRP beats any static at AD >= 81
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  distance eigrp 80 170
```

**Named-mode EIGRP AD syntax:**
```
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  distance eigrp <internal-AD> <external-AD>
```
This replaces the per-neighbor `distance` command used in classic mode.

### Split Horizon

Split horizon is a loop-prevention mechanism for distance-vector protocols. The rule is simple: **do not advertise a route back out the interface it was learned from**.

Without split horizon, a hub router could advertise spoke A's route back to spoke A, creating unnecessary topology entries and potential count-to-infinity conditions in failure scenarios.

In EIGRP Named Mode, split horizon is enabled by default on all interfaces and is configured per interface under `af-interface`:

```
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  af-interface FastEthernet0/0
   no split-horizon       ! disable for hub-spoke multipoint scenarios
  exit-af-interface
```

**When to disable split horizon:**
Split horizon is most problematic in hub-spoke topologies where the hub uses a **single interface** to reach multiple spokes (e.g., Frame Relay multipoint, mGRE/DMVPN). In this case, routes learned from Spoke A via that interface are not re-advertised to Spoke B on the same interface — breaking spoke-to-spoke connectivity through the hub.

In point-to-point topologies (one dedicated interface per neighbor), split horizon rarely causes problems because each neighbor uses a separate interface.

**Verifying split horizon status:**
```
show ip eigrp interfaces detail FastEthernet0/0
! Look for: "Split-horizon enabled" or "Split-horizon disabled"
```

### Route Preference Resolution

When two routes share the same AD, IOS selects based on metric. When AD differs, the lower AD wins unconditionally regardless of metric. This is the fundamental rule:

1. Lower AD → installed in RIB (metric is irrelevant across different AD values)
2. Same AD → lower metric wins
3. Same AD, same metric → ECMP (both installed, load-balanced)

**Skills this lab develops:**

| Skill | Description |
|-------|-------------|
| AD manipulation | Modify EIGRP internal and external AD to shift route preference |
| Floating static design | Configure static backup routes that activate only on dynamic route loss |
| Split horizon analysis | Identify split horizon behavior from topology tables |
| Split horizon tuning | Disable split horizon on hub interfaces for hub-spoke reachability |
| Route preference troubleshooting | Diagnose why a route is or is not in the RIB |

---

## 2. Topology & Scenario

As a lead network engineer at AcmeCorp, you are investigating two operational issues on the EIGRP network:

**Issue 1 — Static backup not behaving as expected at Branch A (R2):** A floating static route was added to provide backup connectivity to R4's loopback (10.0.0.4/32) via Branch B (R3). The operations team reports the route is active in the routing table under normal EIGRP operation, when it should only activate on EIGRP failure. EIGRP's AD must be tuned.

**Issue 2 — Hub route suppression:** A monitoring tool shows that R1 is not re-advertising certain Branch A prefixes back toward Branch A on the Fa0/0 link, even though this would be harmless given the current point-to-point topology. The network team wants to observe the split horizon mechanism directly and disable it on R1's Fa0/0 for future DMVPN readiness.

```
              ┌──────────────────────────────┐
              │            R1                │
              │        (Hub / Core)          │
              │      Lo0: 10.0.0.1/32        │
              └───┬────────────┬────────┬────┘
          Fa0/0  │            │ Fa1/0  │ Fa1/1
    10.12.0.1/30 │            │ 10.13.0.1/30 │ 10.14.0.1/30
                 │            │        │
    10.12.0.2/30 │            │ 10.13.0.2/30 │ 10.14.0.2/30
          Fa0/0  │            │  Fa0/0 │ Fa0/0
  ┌──────────────┘            └────────┼──────────────────────┐
  │                                   │                        │
┌─┴────────────────┐       ┌──────────┘       ┌──────────────┴──┐
│       R2         │       │       R3          │       R4        │
│   (Branch A)     │       │   (Branch B)      │  (Stub / Edge)  │
│ Lo0: 10.0.0.2/32 │       │ Lo0: 10.0.0.3/32  │ Lo0: 10.0.0.4/32│
│ Lo1: 172.16.20/24│       │ Lo1: 172.16.30/24 │ Lo1: 192.168.4/24│
│ Lo2: 172.16.21/24│       │ Lo2: 172.16.31/24 │                 │
└────────┬─────────┘       └────────┬──────────┘                 │
     Fa0/1│                         │Fa0/1                        │
10.23.0.1/30│                     │10.23.0.2/30                   │
             └───────────────────┘                                │
                   10.23.0.0/30                                   │
                                              Floating static: ──→┘
                                   R2: ip route 10.0.0.4/32 via R3 AD 90
```

**Active devices:** R1, R2, R3, R4
**Active links:** L1 (R1↔R2), L2 (R1↔R3), L3 (R2↔R3), L4 (R1↔R4)

---

## 3. Hardware & Environment Specifications

### Cabling Table

| Link ID | Source | Source Interface | Target | Target Interface | Subnet (IPv4) |
|---------|--------|-----------------|--------|-----------------|---------------|
| L1 | R1 | Fa0/0 | R2 | Fa0/0 | 10.12.0.0/30 |
| L2 | R1 | Fa1/0 | R3 | Fa0/0 | 10.13.0.0/30 |
| L3 | R2 | Fa0/1 | R3 | Fa0/1 | 10.23.0.0/30 |
| L4 | R1 | Fa1/1 | R4 | Fa0/0 | 10.14.0.0/30 |

### Console Access Table

| Device | Role | Platform | Console Port | Connection Command |
|--------|------|----------|-------------|-------------------|
| R1 | Hub / Core | c7200 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | Branch A | c7200 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | Branch B | c7200 | 5003 | `telnet 127.0.0.1 5003` |
| R4 | Stub / Edge | c7200 | 5004 | `telnet 127.0.0.1 5004` |

---

## 4. Base Configuration

The following is pre-loaded in `initial-configs/` (identical to Lab 07 solutions):

**Pre-loaded on all routers:**
- Hostnames, `no ip domain-lookup`, `ipv6 unicast-routing`
- Interface IP addresses (IPv4 + IPv6) and `no shutdown`
- Console/VTY access with telnet transport
- EIGRP Named Mode (AS 100) — both IPv4 and IPv6 address families
- R1: prefix-list PFX_DENY_R4_STUB; distribute-list filtering 192.168.4.0/24 outbound
- R2: prefix-list PFX_BRANCH_A_SUMMARY; route-map RM_TAG_BRANCH_A with tag 200; summarization on Fa0/0 and Fa0/1; distribute-list using route-map outbound
- R3: prefix-list PFX_DENY_R4_STUB; distribute-list filtering 192.168.4.0/24 inbound from R1
- R4: EIGRP stub (connected summary); route-map RM_DENY_TAG_200; distribute-list blocking tagged routes inbound
- R1: `variance 5` for unequal-cost load balancing (from Lab 04)

**NOT pre-configured (your tasks):**
- Administrative Distance modification on any router
- Floating static routes
- Split horizon changes on any interface

---

## 5. Lab Challenge: Core Implementation

> AcmeCorp's EIGRP network is stable from prior labs. Your task is to tune administrative distance values and split horizon behavior to meet the operational requirements described above. No step-by-step IOS commands are provided — work from the objectives.

### Task 1: Audit the Default EIGRP Administrative Distance

- On R1 and R2, examine the currently configured administrative distance for EIGRP internal and external routes
- Confirm that all EIGRP routes in R2's routing table are installed at the default EIGRP internal AD
- Record the current AD values — they will be your baseline for the tasks below

**Verification:** `show ip protocols` on R1 and R2 — confirm "Distance: internal 90 external 170"; `show ip route` on R2 — confirm all EIGRP routes show [90/...].

---

### Task 2: Configure a Floating Static Route on R2

- On R2, add a static route to R4's loopback (10.0.0.4/32) with next-hop R3 (10.23.0.2) at administrative distance 90
- This AD value is chosen to compete directly with EIGRP's default internal AD
- Verify which route — EIGRP or static — wins and explain why based on AD and metric rules
- Predict what would happen if the AD were raised to 91 instead

**Verification:** `show ip route 10.0.0.4` on R2 — identify source (D or S) and the [AD/metric] values; `show ip route static` — confirm the static entry exists.

---

### Task 3: Lower EIGRP Internal AD to Restore EIGRP Preference

- On R2, change the EIGRP Named Mode internal administrative distance so that EIGRP routes are preferred over the static route configured in Task 2
- Choose a value that makes the static route a true floating backup (inactive under normal EIGRP operation but ready to activate if the EIGRP route is lost)
- Verify that R2's routing table now shows the EIGRP route to 10.0.0.4/32, and that the static route is present in the config but absent from the RIB

**Verification:** `show ip route 10.0.0.4` on R2 — must show `D` (EIGRP) at the new lower AD; `show running-config | section router eigrp` on R2 — confirm `distance eigrp` is present.

---

### Task 4: Observe and Disable Split Horizon on R1 Fa0/0

- On R1, verify that split horizon is currently enabled on FastEthernet0/0 (the link toward R2)
- Examine R2's EIGRP topology table to see what routes R1 is currently advertising to R2, and confirm that routes R1 learned from R2 are NOT being re-sent back to R2
- Disable split horizon on R1's Fa0/0 interface within the EIGRP Named Mode address family
- After disabling, verify the topology change: R2 should now see its own loopback prefix (10.0.0.2/32) appearing in the EIGRP topology table as learned from R1, in addition to its local entry

**Verification:** `show ip eigrp interfaces detail FastEthernet0/0` on R1 — confirm "Split-horizon disabled"; `show ip eigrp topology 10.0.0.2/32` on R2 — confirm an additional entry via R1 (10.12.0.1) appears alongside the local entry.

---

## 6. Verification & Analysis

### Task 1: Default AD Baseline

```
R1# show ip protocols
*** IP Routing is NSF aware ***
Routing Protocol is "eigrp 100"
  ...
  Distance: internal 90 external 170   ! ← confirm defaults before any changes
```

```
R2# show ip route eigrp
D    10.0.0.1/32 [90/130816] via 10.12.0.1, 00:xx:xx, FastEthernet0/0  ! ← AD=90 (default)
D    10.0.0.3/32 [90/131072] via 10.13.0.2, 00:xx:xx, FastEthernet0/1  ! ← AD=90
D    10.0.0.4/32 [90/131072] via 10.12.0.1, 00:xx:xx, FastEthernet0/0  ! ← AD=90
```

### Task 2: Floating Static at AD 90

```
R2# show ip route 10.0.0.4
Routing entry for 10.0.0.4/32
  Known via "static", distance 90, metric 0               ! ← static wins: same AD (90), lower metric (0 < EIGRP metric)
  Routing Descriptor Blocks:
  * 10.23.0.2, via FastEthernet0/1
      Route metric is 0, traffic share count is 1
```

```
R2# show ip route static
S    10.0.0.4/32 [90/0] via 10.23.0.2                     ! ← AD 90, metric 0 — active in RIB
```

### Task 3: EIGRP AD Lowered to 80

```
R2# show ip route 10.0.0.4
Routing entry for 10.0.0.4/32
  Known via "eigrp 100", distance 80, metric 131072        ! ← EIGRP now wins (AD 80 < static AD 90)
  ...
  * 10.12.0.1, from 10.12.0.1, via FastEthernet0/0
```

```
R2# show running-config | section router eigrp
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  distance eigrp 80 170                                    ! ← confirmed
  ...
```

### Task 4: Split Horizon Disabled on R1 Fa0/0

```
R1# show ip eigrp interfaces detail FastEthernet0/0
EIGRP-IPv4 VR(ENARSI) Address-Family Interfaces for AS(100)
                        Xmit Queue   PeerQ        Mean   Pacing Time   Multicast    Pending
Interface        Peers  Un/Reliable  Un/Reliable  SRTT   Un/Reliable   Flow Timer   Routes
Fa0/0              1        0/0       0/0          10        0/1           50           0
  Hello-interval is 5, Hold-time is 15
  Split-horizon is disabled                        ! ← confirmed after Task 4
  ...
```

```
R2# show ip eigrp topology 10.0.0.2/32
EIGRP-IPv4 VR(ENARSI) Topology Entry for AS(100)/ID(10.0.0.2) for 10.0.0.2/32
State is Passive, Query origin flag is 1, 1 Successor(s), FD is 0
Descriptor Blocks:
0.0.0.0 (Loopback0), from Local, Send flag is 0x0
    Composite metric is (0/0), route is Local       ! ← R2's own local route
10.12.0.1 (FastEthernet0/0), from 10.12.0.1, Send flag is 0x0
    Composite metric is (305152/130816), route is Successor  ! ← now visible after split-horizon disabled
```

---

## 7. Verification Cheatsheet

### Administrative Distance

```
! Named mode — change EIGRP internal and external AD
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  distance eigrp <internal> <external>
```

| Command | Purpose |
|---------|---------|
| `distance eigrp 80 170` | Lower internal AD to 80; external stays 170 |
| `distance eigrp 255 255` | Prevent ALL EIGRP routes from entering RIB (troubleshooting) |
| `ip route <net> <mask> <nh> <AD>` | Static route with custom AD |
| `show ip protocols` | Show current EIGRP distance values |
| `show ip route <prefix>` | Show which source won the RIB and at what AD |
| `show ip route static` | List all static routes |

> **Exam tip:** AD 255 is "administratively prohibited" — no route at AD 255 ever enters the routing table. It is a valid troubleshooting tool to temporarily hide a routing source.

### Split Horizon

```
! Named mode — disable per interface
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  af-interface <interface>
   no split-horizon
  exit-af-interface
```

| Command | Purpose |
|---------|---------|
| `no split-horizon` | Disable under af-interface (named mode) |
| `split-horizon` | Re-enable (restores default) |
| `show ip eigrp interfaces detail <intf>` | Shows "Split-horizon is enabled/disabled" |
| `show ip eigrp topology all-links` | Shows all topology entries including non-successor paths |
| `show ip eigrp topology <prefix>` | Shows all paths to a specific prefix |

> **Exam tip:** Disabling split horizon on a hub interface increases routing update size and EIGRP convergence time — it should only be done where necessary (multipoint hub-spoke). Always re-evaluate after topology changes.

### Verification Commands

| Command | What to Look For |
|---------|-----------------|
| `show ip protocols` | "Distance: internal X external Y" — confirm AD values |
| `show ip route <prefix>` | Source letter (D=EIGRP, S=static) and [AD/metric] |
| `show ip route static` | All static routes with their AD/metric |
| `show ip eigrp interfaces detail <intf>` | "Split-horizon is enabled/disabled" |
| `show ip eigrp topology <prefix>` | All EIGRP topology entries for a prefix |
| `show ip eigrp topology all-links` | Full topology including non-successor paths |

### Common EIGRP Failure Causes

| Symptom | Likely Cause |
|---------|-------------|
| Static route active instead of EIGRP | EIGRP internal AD raised above static AD |
| All EIGRP routes missing from RIB | `distance eigrp 255 255` configured |
| Routes learned via suboptimal path | AD or metric misconfiguration — always check `show ip protocols` first |
| Split horizon "enabled" in topology but no loop | Topology is point-to-point — split horizon works correctly |
| Spoke-to-spoke traffic hairpins through hub | Split horizon enabled on hub multipoint interface — disable with `no split-horizon` |

---

## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these solutions first!

### Task 2: Floating Static Route on R2

<details>
<summary>Click to view R2 Configuration</summary>

```bash
! Add to R2 global config (Task 2 — AD 90 static, competes with EIGRP default AD 90)
ip route 10.0.0.4 255.255.255.255 10.23.0.2 90

! At this point, show ip route 10.0.0.4 shows S [90/0] because
! static metric (0) < EIGRP metric (131072) at the same AD (90)
```

</details>

### Task 3: Lower EIGRP Internal AD on R2

<details>
<summary>Click to view R2 Configuration</summary>

```bash
! R2 — named mode EIGRP, lower internal AD to 80
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  distance eigrp 80 170
 exit-address-family
```

</details>

<details>
<summary>Click to view Verification</summary>

```bash
R2# show ip route 10.0.0.4
! Must show: Known via "eigrp 100", distance 80, metric 131072
! Source = D (EIGRP), not S (static)

R2# show ip route static
! Static route still exists in config but not active in RIB (AD 90 > EIGRP 80)
! ip route 10.0.0.4 255.255.255.255 10.23.0.2 90 — listed but not marked as best
```

</details>

### Task 4: Disable Split Horizon on R1 Fa0/0

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1 — disable split horizon on Fa0/0 (toward R2)
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  af-interface FastEthernet0/0
   no split-horizon
  exit-af-interface
 exit-address-family
```

</details>

<details>
<summary>Click to view Verification</summary>

```bash
R1# show ip eigrp interfaces detail FastEthernet0/0
! Must show: Split-horizon is disabled

R2# show ip eigrp topology 10.0.0.2/32
! Must show TWO entries:
!   1. 0.0.0.0 (Loopback0), from Local — R2's own route
!   2. 10.12.0.1 (FastEthernet0/0), from 10.12.0.1 — now advertised back by R1
```

</details>

---

## 9. Troubleshooting Scenarios

Each ticket simulates a real-world fault. Inject the fault first, then diagnose and fix using only show commands.

### Workflow

```bash
python3 setup_lab.py                                   # reset to known-good state
python3 scripts/fault-injection/inject_scenario_01.py  # Ticket 1
python3 scripts/fault-injection/apply_solution.py      # restore after each ticket
```

---

### Ticket 1 — Branch A Is Routing Traffic to R4 via an Unexpected Path

The NOC has raised an alert: traffic from R2 destined for R4's management loopback (10.0.0.4/32) is traversing Branch B (R3) instead of going directly through the hub. Latency to R4 has increased. EIGRP adjacencies are all up.

**Inject:** `python3 scripts/fault-injection/inject_scenario_01.py`

**Success criteria:** `show ip route 10.0.0.4` on R2 shows EIGRP (`D`) at AD 80, via R1 (10.12.0.1), not the static route via 10.23.0.2.

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
R2# show ip route 10.0.0.4
! Observe: S [90/0] via 10.23.0.2 — static is active instead of EIGRP
! This means EIGRP's AD has been raised above 90

R2# show ip protocols
! Look at: Distance: internal X external Y
! If X >= 91, EIGRP internal AD is too high — static at AD 90 wins

R2# show running-config | section router eigrp
! Confirm the distance eigrp command that caused the fault
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! R2 — restore EIGRP internal AD to 80
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  distance eigrp 80 170
 exit-address-family

! Verify
R2# show ip route 10.0.0.4
! Must show: D [80/...] via 10.12.0.1, FastEthernet0/0
```

</details>

---

### Ticket 2 — R2 Has Lost All EIGRP Routes

An operator reports that R2 cannot reach R3's loopback (10.0.0.3/32) or R4's loopback (10.0.0.4/32). The `show ip eigrp neighbors` command on R2 shows R1 as an active neighbor, so the EIGRP adjacency itself is intact.

**Inject:** `python3 scripts/fault-injection/inject_scenario_02.py`

**Success criteria:** `show ip route eigrp` on R2 shows all expected EIGRP routes (10.0.0.1, 10.0.0.3, 10.0.0.4, transit subnets) at AD 80.

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
R2# show ip eigrp neighbors
! Neighbors are UP — adjacency is fine, so the problem is not a hello/hold-time fault

R2# show ip route eigrp
! Output is empty — no EIGRP routes in RIB despite active adjacency

R2# show ip protocols
! Look for: Distance: internal 255 external 255
! AD 255 = "do not install" — all EIGRP routes are filtered from the RIB

R2# show running-config | section router eigrp
! Confirm: distance eigrp 255 255
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! R2 — restore correct EIGRP AD
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  distance eigrp 80 170
 exit-address-family

! Verify
R2# show ip route eigrp
! Must show D [80/...] entries for all remote loopbacks and transit subnets
R2# ping 10.0.0.3 source loopback 0
! Must succeed
```

</details>

---

### Ticket 3 — Branch A and Branch B Cannot Reach Each Other's Loopbacks Through R1

The NOC reports that pings between R2's loopback (10.0.0.2) and R3's loopback (10.0.0.3) fail when forced through R1 as the transit router. Both R2 and R3 show R1 as an active EIGRP neighbor and have R1's loopback (10.0.0.1) in their routing tables. R1's adjacencies to R2, R3, and R4 are all up.

**Inject:** `python3 scripts/fault-injection/inject_scenario_03.py`

**Success criteria:** `show ip route 10.0.0.2` on R3 shows a valid EIGRP route via R1; `ping 10.0.0.3 source lo0` from R2 succeeds via R1.

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
R2# show ip route 10.0.0.3
! Shows EIGRP route [80/...] — R2 has the route

R1# show ip route eigrp
! Output is empty or missing remote loopback entries
! R1 itself has no EIGRP routes — it cannot forward between R2 and R3 for remote prefixes

R1# show ip protocols
! Look for: Distance: internal 255 external 255
! R1's EIGRP AD is 255 — R1 forms adjacencies (EIGRP control plane is intact)
! but refuses to install any EIGRP route in its own RIB (data plane broken)

R1# show running-config | section router eigrp
! Confirm: distance eigrp 255 255
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! R1 — restore correct EIGRP AD
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  distance eigrp 80 170
 exit-address-family

! Verify
R1# show ip route eigrp
! Must show all remote loopbacks and transit subnets as EIGRP routes

R2# ping 10.0.0.3 source loopback 0
! Must succeed (5/5 packets)
```

</details>

---

## 10. Lab Completion Checklist

### Core Implementation

- [ ] Task 1: Confirmed default EIGRP internal AD = 90 and external AD = 170 on R1 and R2 via `show ip protocols`
- [ ] Task 2: Floating static route to 10.0.0.4/32 at AD 90 added on R2; confirmed static [90/0] wins over EIGRP [90/large-metric] at default AD
- [ ] Task 3: EIGRP internal AD changed to 80 on R2 via `distance eigrp 80 170`; confirmed EIGRP route D [80/...] is now active and static is dormant
- [ ] Task 4: Split horizon disabled on R1 Fa0/0 via `no split-horizon` under af-interface; confirmed "Split-horizon is disabled" in `show ip eigrp interfaces detail`; confirmed R2's own loopback appears in R2's EIGRP topology as learned from R1

### Troubleshooting Scenarios

- [ ] Ticket 1: Diagnosed EIGRP internal AD raised above 90 on R2 causing static to take over; restored `distance eigrp 80 170`
- [ ] Ticket 2: Diagnosed `distance eigrp 255 255` on R2 causing all EIGRP routes to be dropped from RIB; restored correct AD
- [ ] Ticket 3: Diagnosed `distance eigrp 255 255` on R1 causing R1 to forward-fail between branches despite active adjacencies; restored correct AD
