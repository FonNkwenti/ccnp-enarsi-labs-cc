# CCNP ENARSI Lab 05 — EIGRP Summarization: Manual and Auto-Summary

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

**Exam Objective:** 1.5 — Troubleshoot manual and auto-summarization with EIGRPv4 and EIGRPv6

EIGRP summarization reduces the number of prefixes advertised across routing domain boundaries, shrinking routing tables, accelerating convergence, and localizing topology changes. This lab explores how Named Mode EIGRP implements interface-level manual summarization, why it automatically installs a Null0 discard route, and the failure modes that arise when summarization is misconfigured.

---

### Route Summarization Fundamentals

Summarization aggregates a group of more-specific prefixes into a single covering prefix that is advertised to neighbors. When a router running EIGRP is configured to summarize, it:

1. **Suppresses the specific prefixes** — neighbors no longer receive the individual /24s
2. **Advertises a single covering prefix** — e.g., 172.16.20.0/23 instead of 172.16.20.0/24 + 172.16.21.0/24
3. **Installs a local Null0 discard route** — to prevent routing loops when traffic matches the summary but no more-specific route exists

Summarization is most beneficial at topology boundaries: branch offices summarizing their loopback networks toward the hub, or redistribution points summarizing internal space before injecting into BGP.

---

### Named Mode EIGRP — af-interface Summary Configuration

In classic EIGRP mode the summary command lived under the interface:
```
interface FastEthernet0/0
 ip summary-address eigrp 100 172.16.20.0 255.255.254.0
```

In Named Mode EIGRP (the standard from IOS 15.x onward), interface-level EIGRP attributes are configured inside an `af-interface` block under the address-family:

```
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  af-interface FastEthernet0/0
   summary-address 172.16.20.0 255.255.254.0
  exit-af-interface
 exit-address-family
```

Key rules:
- The summary must be configured **per outgoing interface** — it only suppresses specific routes on that interface, not globally
- If a branch has two outgoing links (e.g., toward hub and toward a peer), the summary must be applied on **both** interfaces to prevent specific routes from leaking via the other path
- The summary is advertised with the **lowest metric** among all contributing specific routes

---

### The Null0 Discard Route

Whenever EIGRP installs a summary route, IOS automatically adds a local Null0 entry for that prefix with Administrative Distance = 5:

```
D     172.16.20.0/23 [5/0] via Null0
```

**Why AD = 5?** This is lower than any normal routing protocol AD (EIGRP internal = 90), so the Null0 entry is only used when no more-specific route exists. If one of the summarized /24s goes down, traffic destined for that subnet matches the summary → hits Null0 → is dropped cleanly rather than looping.

**The black-hole risk:** If a summarized prefix is advertised but the router has no more-specific route in its table (e.g., a loopback interface is shutdown or its network statement is missing), remote hosts believe the prefix is reachable via the summarizing router, but the router silently drops the traffic against Null0.

---

### Auto-Summary in Named Mode

Auto-summary classfully collapses subnets at major network boundaries (class A/B/C boundaries). It is **disabled by default** in Named Mode EIGRP and should remain disabled in all modern designs. Enabling it causes problems with discontiguous networks:

- If 172.16.20.0/24 and 172.16.21.0/24 exist on different routers that are not directly connected, auto-summary on both routers advertises the classful 172.16.0.0/16, causing traffic to loop or be dropped at the wrong router.

Verify auto-summary is off:
```
show ip protocols | include auto
```
Expected: `Automatic summarization: disabled`

| Setting | Effect |
|---------|--------|
| `no auto-summary` | Specific prefixes advertised (default, correct) |
| `auto-summary` | Classful summarization at major boundaries (legacy, avoid) |

---

### Summary Mask Selection

To summarize 172.16.20.0/24 and 172.16.21.0/24 into a single prefix:

| Address | Binary (last two octets) |
|---------|--------------------------|
| 172.16.20.0 | 0001 0100 . 0000 0000 |
| 172.16.21.0 | 0001 0101 . 0000 0000 |
| Common bits | 0001 010**x** (first 23 bits match) |
| Summary | 172.16.20.0 **/23** |
| Mask | 255.255.254.0 |

Similarly: 172.16.30.0/24 + 172.16.31.0/24 → 172.16.30.0**/23** (mask 255.255.254.0)

---

**Skills this lab develops:**

| Skill | Description |
|-------|-------------|
| Named mode af-interface | Configure EIGRP attributes at the interface level within address-family |
| Manual summarization | Aggregate specific prefixes into a covering route |
| Summary mask calculation | Identify the correct covering prefix and mask |
| Null0 discard route | Understand and predict local discard route installation |
| Summarization black hole | Diagnose and resolve traffic drop at summarizing router |
| Auto-summary pitfalls | Identify discontiguous network issues caused by auto-summary |

---

## 2. Topology & Scenario

As the lead network engineer at Acme Corporation, you have just completed the loop-free path selection work across the WAN triangle (R1 hub, R2 Branch-A, R3 Branch-B). Management has asked you to optimize the routing tables across the network — each branch runs two dedicated loopback networks simulating internal LAN segments, and R1's routing table is growing with individual /24 prefixes. Your task is to configure manual EIGRP summarization on the branch routers so that each branch advertises a single summary to its peers, reducing route churn and table size while maintaining full reachability.

```
              ┌──────────────────────────┐
              │            R1            │
              │       (Hub / Core)       │
              │    Lo0: 10.0.0.1/32      │
              └──────┬────────────┬──────┘
           Fa0/0     │            │     Fa1/0
     10.12.0.1/30    │            │   10.13.0.1/30
                     │            │
     10.12.0.2/30    │            │   10.13.0.2/30
           Fa0/0     │            │     Fa0/0
     ┌───────────────┘            └────────────────┐
     │                                             │
┌────┴──────────────────┐       ┌──────────────────┴────┐
│          R2           │       │          R3            │
│      (Branch A)       │       │      (Branch B)        │
│  Lo0: 10.0.0.2/32     │       │  Lo0: 10.0.0.3/32      │
│  Lo1: 172.16.20.1/24  │       │  Lo1: 172.16.30.1/24   │
│  Lo2: 172.16.21.1/24  │       │  Lo2: 172.16.31.1/24   │
│  Advertises:          │       │  Advertises:           │
│  172.16.20.0/23 →     │       │  172.16.30.0/23 →      │
└──────────┬────────────┘       └────────────┬───────────┘
       Fa0/1│                               │Fa0/1
  10.23.0.1/30│                           │10.23.0.2/30
               └───────────────────────────┘
                         10.23.0.0/30
```

---

## 3. Hardware & Environment Specifications

### Router Platform

| Device | Platform | IOS Image | Role |
|--------|----------|-----------|------|
| R1 | Cisco c7200 | c7200-adventerprisek9-mz.153-3.XB12.image | Hub / Core |
| R2 | Cisco c7200 | c7200-adventerprisek9-mz.153-3.XB12.image | Branch A |
| R3 | Cisco c7200 | c7200-adventerprisek9-mz.153-3.XB12.image | Branch B |

### Adapter Cards

| Device | Slot | Card | Interfaces |
|--------|------|------|------------|
| R1 | 0 | C7200-IO-FE | Fa0/0 |
| R1 | 1 | PA-2FE-TX | Fa1/0, Fa1/1 |
| R2 | 0 | C7200-IO-2FE | Fa0/0, Fa0/1 |
| R3 | 0 | C7200-IO-2FE | Fa0/0, Fa0/1 |

### Cabling Table

| Link ID | Source | Destination | IPv4 Subnet | IPv6 Subnet |
|---------|--------|-------------|-------------|-------------|
| L1 | R1 Fa0/0 (10.12.0.1/30) | R2 Fa0/0 (10.12.0.2/30) | 10.12.0.0/30 | 2001:db8:12::/64 |
| L2 | R1 Fa1/0 (10.13.0.1/30) | R3 Fa0/0 (10.13.0.2/30) | 10.13.0.0/30 | 2001:db8:13::/64 |
| L3 | R2 Fa0/1 (10.23.0.1/30) | R3 Fa0/1 (10.23.0.2/30) | 10.23.0.0/30 | 2001:db8:23::/64 |

### Console Access Table

| Device | Port | Connection Command |
|--------|------|--------------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |

---

## 4. Base Configuration

The `initial-configs/` directory contains configurations carried forward from Lab 04 solutions. The following is **pre-configured** on all routers:

**Pre-configured:**
- Hostnames, `no ip domain-lookup`, `ipv6 unicast-routing`
- All physical interface IP addresses (IPv4 and IPv6)
- Loopback0 on R1, R2, and R3 (router-ID interfaces)
- Named mode EIGRP (`router eigrp ENARSI`) with IPv4 and IPv6 address families
- EIGRP network statements for all transit subnets and Loopback0 addresses
- EIGRP router-IDs, `no auto-summary`
- `eigrp log-neighbor-changes`
- R1 Fa0/0: `bandwidth 512`, `delay 2000` (retained from Lab 03 metric tuning)
- R1 IPv4 AF: `variance 5` (retained from Lab 04 unequal-cost load balancing)

**NOT pre-configured (student tasks):**
- Loopback1 and Loopback2 interfaces on R2 and R3
- EIGRP network statements for the new loopback subnets
- Manual summarization (`af-interface summary-address`) on any router

---

## 5. Lab Challenge: Core Implementation

> Your task: optimize the Acme WAN routing table by adding branch loopback networks and configuring EIGRP summarization so that each branch advertises a single covering prefix.

---

### Task 1: Add Branch Loopback Interfaces and Advertise into EIGRP

- On R2, create two additional loopback interfaces: one in the 172.16.20.0/24 range (IP ending in .1) and one in the 172.16.21.0/24 range (IP ending in .1)
- On R3, create two additional loopback interfaces: one in the 172.16.30.0/24 range (IP ending in .1) and one in the 172.16.31.0/24 range (IP ending in .1)
- Include all four new loopback subnets in the EIGRP IPv4 address family on the respective routers using the appropriate network statements

**Verification:** `show ip route eigrp` on R1 must show four new EIGRP-learned /24 entries: two from R2 (via 10.12.0.2) and two from R3 (via 10.13.0.2). `show ip eigrp neighbors` should remain stable — no adjacency resets.

---

### Task 2: Configure Manual Summarization on R2

- Calculate the smallest single covering prefix that includes both 172.16.20.0/24 and 172.16.21.0/24
- Configure a summary-address for that covering prefix on each of R2's outgoing EIGRP interfaces using the Named Mode `af-interface` syntax
- Apply the summary on **both** outgoing interfaces (toward R1 and toward R3) so that no neighbor receives the individual /24 routes

**Verification:** `show ip route eigrp` on R1 must show a single EIGRP route for the 172.16.20.0/23 range (not two /24s). `show ip route` on R2 must show the local Null0 discard entry for the summary prefix. `show ip eigrp topology` on R1 must list the summary as a successor route via R2.

---

### Task 3: Configure Manual Summarization on R3

- Calculate the smallest single covering prefix that includes both 172.16.30.0/24 and 172.16.31.0/24
- Configure a summary-address for that covering prefix on each of R3's outgoing EIGRP interfaces using the Named Mode `af-interface` syntax
- Apply the summary on both outgoing interfaces (toward R1 and toward R2)

**Verification:** `show ip route eigrp` on R1 must show a single EIGRP route for the 172.16.30.0/23 range. `show ip route` on R3 must show the Null0 discard entry. Confirm end-to-end reachability: from R1, ping 172.16.30.1 and 172.16.31.1 — both must succeed.

---

### Task 4: Observe and Explain the Null0 Discard Route

- On R2, display the routing table entry for the 172.16.20.0/23 prefix and identify its Administrative Distance, metric, and next-hop
- On R3, do the same for 172.16.30.0/23
- Explain in your notes: (a) what event causes Null0 to be used in practice, (b) why the AD of this entry is set unusually low, and (c) what would happen to traffic destined for 172.16.21.0/24 if R2's Loopback2 interface were shut down

**Verification:** `show ip route 172.16.20.0 255.255.254.0` on R2 must show `[5/0] via Null0`. `show ip route 172.16.30.0 255.255.254.0` on R3 must show `[5/0] via Null0`. `show ip protocols | include auto` on all routers must confirm `Automatic summarization: disabled`.

---

## 6. Verification & Analysis

### Task 1 — New Loopbacks Advertised into EIGRP

```
R1# show ip route eigrp
...
D     10.0.0.2/32 [90/130816] via 10.12.0.2, Fa0/0
D     10.0.0.3/32 [90/130816] via 10.13.0.2, Fa1/0
D     172.16.20.0/24 [90/130816] via 10.12.0.2, Fa0/0   ! ← R2 Lo1 learned before summarization
D     172.16.21.0/24 [90/130816] via 10.12.0.2, Fa0/0   ! ← R2 Lo2 learned before summarization
D     172.16.30.0/24 [90/130816] via 10.13.0.2, Fa1/0   ! ← R3 Lo1 learned before summarization
D     172.16.31.0/24 [90/130816] via 10.13.0.2, Fa1/0   ! ← R3 Lo2 learned before summarization
```

### Task 2 — R2 Summary Visible on R1

```
R1# show ip route eigrp
...
D     10.0.0.2/32 [90/130816] via 10.12.0.2, Fa0/0
D     10.0.0.3/32 [90/130816] via 10.13.0.2, Fa1/0
D     172.16.20.0/23 [90/130816] via 10.12.0.2, 00:00:45, Fa0/0   ! ← summary replaces two /24s
D     172.16.30.0/24 [90/130816] via 10.13.0.2, Fa1/0              ! ← R3 still unsummarized
D     172.16.31.0/24 [90/130816] via 10.13.0.2, Fa1/0

R1# show ip eigrp topology 172.16.20.0/23
EIGRP-IPv4 Topology Entry for AS(100)/ID(10.0.0.1) for 172.16.20.0/23
  State is Passive, Query origin flag is 1, 1 Successor(s), FD is 130816
  Descriptor Blocks:
  10.12.0.2 (FastEthernet0/0), from 10.12.0.2, Send flag is 0x0
      Composite metric is (130816/128256), route is Internal   ! ← FD/RD for summary
      Vector metric:
        ...
```

### Task 2 — Null0 Discard on R2

```
R2# show ip route 172.16.20.0 255.255.254.0
Routing entry for 172.16.20.0/23
  Known via "eigrp 100", distance 5, metric 0, type internal   ! ← AD=5, Null0 entry
  Routing Descriptor Blocks:
  * directly connected, via Null0
      Route metric is 0, traffic share count is 1

R2# show ip route | include Null0
D     172.16.20.0/23 [5/0] via Null0                            ! ← discard route present
```

### Task 3 — Both Summaries Visible on R1

```
R1# show ip route eigrp
      10.0.0.0/32 is subnetted, 3 subnets
D        10.0.0.2/32 [90/130816] via 10.12.0.2, Fa0/0
D        10.0.0.3/32 [90/130816] via 10.13.0.2, Fa1/0
      172.16.0.0/23 is subnetted, 2 subnets
D        172.16.20.0/23 [90/130816] via 10.12.0.2, Fa0/0        ! ← Branch-A summary ✓
D        172.16.30.0/23 [90/130816] via 10.13.0.2, Fa1/0        ! ← Branch-B summary ✓

R1# ping 172.16.30.1 source loopback0
!!!!!   ! ← R3 Lo1 reachable through summary
R1# ping 172.16.31.1 source loopback0
!!!!!   ! ← R3 Lo2 reachable through summary
```

### Task 4 — Auto-Summary Disabled

```
R1# show ip protocols | include auto
  Automatic summarization: disabled   ! ← must be disabled on all routers
R2# show ip protocols | include auto
  Automatic summarization: disabled
R3# show ip protocols | include auto
  Automatic summarization: disabled
```

---

## 7. Verification Cheatsheet

### EIGRP Named Mode — af-interface Summary Configuration

```
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  af-interface <interface>
   summary-address <network> <mask>
  exit-af-interface
 exit-address-family
```

| Command | Purpose |
|---------|---------|
| `af-interface <intf>` | Enter interface-level EIGRP attribute block |
| `summary-address <net> <mask>` | Advertise covering prefix, suppress specifics |
| `no summary-address <net> <mask>` | Remove summary (specific routes reappear) |
| `exit-af-interface` | Return to address-family context |

> **Exam tip:** In Named Mode, `summary-address` under `af-interface` replaces the classic `ip summary-address eigrp` interface command. The concept is identical — only the configuration location changes.

### Summarization Verification Commands

| Command | What to Look For |
|---------|-----------------|
| `show ip route eigrp` | Summary prefix replaces individual /24s on neighbors |
| `show ip route <summary> <mask>` | AD=5, metric=0, via Null0 on summarizing router |
| `show ip route | include Null0` | Confirm discard route is installed |
| `show ip eigrp topology <prefix/len>` | Confirm summary is Passive with FD/RD values |
| `show ip protocols | include auto` | Confirm `Automatic summarization: disabled` |
| `show run | section router eigrp` | Inspect full Named Mode config including af-interface blocks |

### Summarization Decision Guide

| Condition | Action |
|-----------|--------|
| Two interfaces toward different neighbors | Apply summary on **both** af-interface blocks |
| Loopback not in routing table | Check `network` statement covers the loopback subnet |
| Summary active but specific unreachable | Check if contributing /24 is down → Null0 black hole |
| Neighbor still receiving /24s | Check if summary is configured on the correct **outgoing** interface |
| Auto-summary causing /16 advertisement | Verify `no auto-summary` in address-family config |

### Wildcard Mask Quick Reference

| Subnet Mask | Wildcard | Common Use |
|-------------|----------|------------|
| 255.255.255.255 | 0.0.0.0 | Host route (loopback) |
| 255.255.255.252 | 0.0.0.3 | /30 point-to-point link |
| 255.255.255.0 | 0.0.0.255 | /24 LAN or loopback network |
| 255.255.254.0 | 0.0.1.255 | /23 two-subnet summary |
| 255.255.0.0 | 0.0.255.255 | /16 classful B summary |

### Common EIGRP Summarization Failure Causes

| Symptom | Likely Cause |
|---------|-------------|
| Neighbor still sees specific /24s | `summary-address` missing on that interface's `af-interface` block |
| Traffic to specific prefix dropped at summarizing router | Contributing loopback down or missing network statement → Null0 black hole |
| Summary not advertised at all | No more-specific routes in routing table that fall within summary range |
| Wrong covering prefix advertised | Incorrect mask calculation (e.g., /24 instead of /23) |
| Individual /24s visible network-wide | Summary only on one outgoing interface; specific routes leak via other path |

---

## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these steps first!

### Task 1: Add Loopback Interfaces and Advertise into EIGRP

<details>
<summary>Click to view R2 Configuration</summary>

```bash
! R2 — Add Lo1, Lo2 and advertise into EIGRP IPv4 AF
interface Loopback1
 description Lo1 - Branch-A LAN segment 1
 ip address 172.16.20.1 255.255.255.0
!
interface Loopback2
 description Lo2 - Branch-A LAN segment 2
 ip address 172.16.21.1 255.255.255.0
!
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  network 172.16.20.0 0.0.0.255
  network 172.16.21.0 0.0.0.255
 exit-address-family
```

</details>

<details>
<summary>Click to view R3 Configuration</summary>

```bash
! R3 — Add Lo1, Lo2 and advertise into EIGRP IPv4 AF
interface Loopback1
 description Lo1 - Branch-B LAN segment 1
 ip address 172.16.30.1 255.255.255.0
!
interface Loopback2
 description Lo2 - Branch-B LAN segment 2
 ip address 172.16.31.1 255.255.255.0
!
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  network 172.16.30.0 0.0.0.255
  network 172.16.31.0 0.0.0.255
 exit-address-family
```

</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
show ip route eigrp          ! R1 — expect 4 new /24 D routes from R2 and R3
show ip eigrp neighbors      ! all routers — no adjacency reset expected
```

</details>

---

### Task 2: Manual Summarization on R2

<details>
<summary>Click to view R2 Configuration</summary>

```bash
! R2 — Configure manual summary 172.16.20.0/23 on both outgoing interfaces
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  af-interface FastEthernet0/0
   summary-address 172.16.20.0 255.255.254.0
  exit-af-interface
  af-interface FastEthernet0/1
   summary-address 172.16.20.0 255.255.254.0
  exit-af-interface
 exit-address-family
```

</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
! On R1 — summary replaces /24s
show ip route eigrp
show ip eigrp topology 172.16.20.0/23

! On R2 — Null0 discard installed
show ip route 172.16.20.0 255.255.254.0
show ip route | include Null0
```

</details>

---

### Task 3: Manual Summarization on R3

<details>
<summary>Click to view R3 Configuration</summary>

```bash
! R3 — Configure manual summary 172.16.30.0/23 on both outgoing interfaces
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  af-interface FastEthernet0/0
   summary-address 172.16.30.0 255.255.254.0
  exit-af-interface
  af-interface FastEthernet0/1
   summary-address 172.16.30.0 255.255.254.0
  exit-af-interface
 exit-address-family
```

</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
! On R1 — both summaries present, no /24s
show ip route eigrp

! On R3 — Null0 discard installed
show ip route 172.16.30.0 255.255.254.0
show ip route | include Null0

! End-to-end reachability
ping 172.16.30.1 source loopback0
ping 172.16.31.1 source loopback0
```

</details>

---

### Task 4: Null0 Discard Route

<details>
<summary>Click to view Verification and Explanation</summary>

```bash
! On R2
R2# show ip route 172.16.20.0 255.255.254.0
Routing entry for 172.16.20.0/23
  Known via "eigrp 100", distance 5, metric 0, type internal
  * directly connected, via Null0

! On R3
R3# show ip route 172.16.30.0 255.255.254.0
  * directly connected, via Null0
```

**Explanation:**
- **When Null0 is used:** Traffic arrives at R2 for a destination within 172.16.20.0/23 but no more-specific /24 route exists (e.g., Lo2 is shutdown). The traffic matches the /23 summary, hits Null0, and is cleanly dropped.
- **Why AD = 5:** Lower than any routing protocol (EIGRP internal = 90), so Null0 is only a last-resort within the summarizing router. Remote routers still forward to R2 because they see the /23 summary with AD = 90.
- **If Lo2 is shut:** R2 loses the 172.16.21.0/24 specific route. Traffic to 172.16.21.0/24 arrives at R2 from R1, matches the /23 Null0, and is dropped — a summarization black hole.

</details>

---

## 9. Troubleshooting Scenarios

Each ticket simulates a real-world fault. Inject the fault first, then
diagnose and fix using only show commands.

### Workflow

```bash
python3 setup_lab.py                                   # reset to known-good state
python3 scripts/fault-injection/inject_scenario_01.py  # Ticket 1
python3 scripts/fault-injection/apply_solution.py      # restore between tickets
```

---

### Ticket 1 — R1's Routing Table Contains Unsummarized Branch-A Routes

A network operations alert shows R1's routing table has grown unexpectedly. Upon inspection, you observe individual /24 entries from Branch-A rather than the single covering prefix that was configured last week.

**Inject:** `python3 scripts/fault-injection/inject_scenario_01.py`

**Success criteria:** After fix, `show ip route eigrp` on R1 must show a single 172.16.20.0/23 entry learned from R2, with no individual /24 prefixes for 172.16.20.0 or 172.16.21.0 visible.

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Step 1 — Confirm the symptom
R1# show ip route eigrp | include 172.16.2
D     172.16.20.0/24 [90/...] via 10.12.0.2, Fa0/0    ! specific /24 present — wrong
D     172.16.21.0/24 [90/...] via 10.12.0.2, Fa0/0    ! specific /24 present — wrong

! Step 2 — Check R2's topology table
R2# show ip eigrp topology | include 172.16.2
! Expect to see no summary entry — summary has been removed

! Step 3 — Inspect R2's af-interface config for Fa0/0
R2# show run | section router eigrp
! Look for af-interface FastEthernet0/0 — summary-address line missing
```

</details>

<details>
<summary>Click to view Fix</summary>

**Root cause:** The `summary-address 172.16.20.0 255.255.254.0` was removed from R2's `af-interface FastEthernet0/0` block.

```bash
R2# conf t
R2(config)# router eigrp ENARSI
R2(config-router)# address-family ipv4 unicast autonomous-system 100
R2(config-router-af)# af-interface FastEthernet0/0
R2(config-router-af-interface)# summary-address 172.16.20.0 255.255.254.0
R2(config-router-af-interface)# exit-af-interface
R2(config-router-af)# exit-address-family

! Verify
R1# show ip route eigrp | include 172.16.20
D     172.16.20.0/23 [90/130816] via 10.12.0.2   ! summary restored
```

</details>

---

### Ticket 2 — 172.16.31.0/24 Unreachable Across the Entire Network

A trouble ticket arrives from Branch-B staff: pings to the second LAN segment (ending in .31.x) fail from all locations, while the first segment (ending in .30.x) works normally.

**Inject:** `python3 scripts/fault-injection/inject_scenario_02.py`

**Success criteria:** After fix, `ping 172.16.31.1 source loopback0` from R1 must succeed with five replies. R3's Null0 discard for 172.16.30.0/23 must remain in place.

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Step 1 — Confirm the symptom
R1# ping 172.16.31.1 source loopback0
.....   ! fails

R1# ping 172.16.30.1 source loopback0
!!!!!   ! succeeds — R3 Lo1 fine

! Step 2 — Check R3's routing table
R3# show ip route 172.16.31.0
% Subnet not in table    ! specific /24 missing on R3 itself

! Step 3 — Check R3's EIGRP topology
R3# show ip eigrp topology | include 172.16.31
! Nothing — prefix not in topology table

! Step 4 — Check R3's Loopback2
R3# show interface loopback2
Loopback2 is up   ! interface is up

! Step 5 — Check EIGRP network statements
R3# show run | section router eigrp
! Look for network 172.16.31.0 0.0.0.255 — it will be missing
```

**Analysis:** R3's Lo2 interface is up but its subnet is not included in EIGRP. R3 advertises the 172.16.30.0/23 summary (because Lo1's /24 keeps it alive), but traffic to 172.16.31.0/24 arrives at R3, finds no more-specific route, hits the Null0 discard — a summarization black hole.

</details>

<details>
<summary>Click to view Fix</summary>

**Root cause:** The `network 172.16.31.0 0.0.0.255` statement was removed from R3's IPv4 address family. R3's Loopback2 has an IP address but EIGRP is not advertising it, so the /24 has no route on R3 and traffic is black-holed at Null0.

```bash
R3# conf t
R3(config)# router eigrp ENARSI
R3(config-router)# address-family ipv4 unicast autonomous-system 100
R3(config-router-af)# network 172.16.31.0 0.0.0.255
R3(config-router-af)# exit-address-family

! Verify
R3# show ip route 172.16.31.0
D     172.16.31.0/24 is directly connected, Loopback2   ! specific route back

R1# ping 172.16.31.1 source loopback0
!!!!!   ! reachable
```

</details>

---

### Ticket 3 — R2 Sees Unsummarized Routes from Branch-B

A junior engineer reports that the routing tables are inconsistent: when checking R2's routing table, individual Branch-B /24 routes are visible from R3, but when checking R1, the correct 172.16.30.0/23 summary appears. R1 and R2 should both see summaries.

**Inject:** `python3 scripts/fault-injection/inject_scenario_03.py`

**Success criteria:** After fix, `show ip route eigrp` on R2 must show a single 172.16.30.0/23 entry from R3 instead of individual /24 prefixes.

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Step 1 — Confirm the symptom
R2# show ip route eigrp | include 172.16.3
D     172.16.30.0/24 [90/...] via 10.23.0.2, Fa0/1    ! specific /24 — wrong
D     172.16.31.0/24 [90/...] via 10.23.0.2, Fa0/1    ! specific /24 — wrong

R1# show ip route eigrp | include 172.16.3
D     172.16.30.0/23 [90/...] via 10.13.0.2, Fa1/0    ! summary present on R1 — correct

! Step 2 — Identify the difference
! R1 receives summary (via Fa1/0 link to R3), R2 receives specifics (via Fa0/1 link to R3)
! R3 must be summarizing on Fa0/0 (toward R1) but NOT on Fa0/1 (toward R2)

! Step 3 — Verify on R3
R3# show run | section router eigrp
! Look for af-interface FastEthernet0/1 — summary-address line will be missing
```

</details>

<details>
<summary>Click to view Fix</summary>

**Root cause:** R3's `summary-address 172.16.30.0 255.255.254.0` was removed from `af-interface FastEthernet0/1` (the R2-facing link). The summary is still applied on Fa0/0 (toward R1), so R1 receives the summary, but specific /24s leak to R2 via the direct R2-R3 link.

```bash
R3# conf t
R3(config)# router eigrp ENARSI
R3(config-router)# address-family ipv4 unicast autonomous-system 100
R3(config-router-af)# af-interface FastEthernet0/1
R3(config-router-af-interface)# summary-address 172.16.30.0 255.255.254.0
R3(config-router-af-interface)# exit-af-interface
R3(config-router-af)# exit-address-family

! Verify
R2# show ip route eigrp | include 172.16.3
D     172.16.30.0/23 [90/...] via 10.23.0.2, Fa0/1   ! summary now present on R2
```

</details>

---

## 10. Lab Completion Checklist

### Core Implementation

- [ ] R2 Loopback1 (172.16.20.1/24) and Loopback2 (172.16.21.1/24) configured and up
- [ ] R3 Loopback1 (172.16.30.1/24) and Loopback2 (172.16.31.1/24) configured and up
- [ ] R2 EIGRP network statements include 172.16.20.0/24 and 172.16.21.0/24
- [ ] R3 EIGRP network statements include 172.16.30.0/24 and 172.16.31.0/24
- [ ] R2 advertises 172.16.20.0/23 summary on both Fa0/0 and Fa0/1
- [ ] R3 advertises 172.16.30.0/23 summary on both Fa0/0 and Fa0/1
- [ ] R1 shows only 172.16.20.0/23 and 172.16.30.0/23 (no individual /24s)
- [ ] R2 and R3 each have a Null0 discard route with AD=5 for their summary
- [ ] All routers confirm `Automatic summarization: disabled`
- [ ] End-to-end reachability: R1 can ping all four loopback addresses (20.1, 21.1, 30.1, 31.1)

### Troubleshooting

- [ ] Ticket 1 resolved: R1 sees 172.16.20.0/23 summary from R2 after fix
- [ ] Ticket 2 resolved: 172.16.31.1 pingable from R1 after restoring R3 network statement
- [ ] Ticket 3 resolved: R2 sees 172.16.30.0/23 summary from R3 on Fa0/1 after fix
