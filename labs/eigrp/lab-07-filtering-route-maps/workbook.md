# CCNP ENARSI Lab 07 — Route Filtering & Route Maps

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

**Exam Objective:** 1.2 — Troubleshoot route map (filtering, tagging) | 1.3 — Troubleshoot loop prevention mechanisms (split horizon, route poisoning)

This lab moves beyond basic EIGRP configuration into the control-plane policy tools that production networks rely on. You will implement prefix-list distribute-lists to surgically filter which routes enter or leave each router's EIGRP update stream, and route-maps to stamp routes with tags for loop prevention — a technique critical in multi-protocol environments where routes can inadvertently circulate between routing domains.

### Prefix Lists

A prefix-list is an ordered sequence of match statements that evaluate an IP prefix (network + mask) against conditions. Each entry is evaluated in sequence-number order. The first matching entry takes effect — permit allows the prefix through, deny blocks it. Like all Cisco access-control constructs, an **implicit deny-all** exists at the end of every prefix-list.

```
ip prefix-list NAME seq 5 deny 192.168.4.0/24
ip prefix-list NAME seq 10 permit 0.0.0.0/0 le 32
```

The `le 32` (less-than-or-equal 32) at sequence 10 matches any prefix of any length — the "permit everything else" catch-all. Without it, every prefix not matching a previous entry is silently dropped.

Prefix-lists support GE/LE range operators:

| Syntax | Matches |
|--------|---------|
| `10.0.0.0/8` | Exactly 10.0.0.0/8 |
| `10.0.0.0/8 ge 24` | Any /24 or longer within 10.0.0.0/8 |
| `10.0.0.0/8 le 16` | Any /16 or shorter within 10.0.0.0/8 |
| `0.0.0.0/0 le 32` | Any prefix, any length (default route + all hosts) |

### Distribute Lists in EIGRP Named Mode

A distribute-list applies a prefix-list, ACL, or route-map as a filter on EIGRP update messages. In named mode EIGRP, distribute-list is configured under the `topology base` sub-mode within the address-family:

```
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  topology base
   distribute-list prefix PREFIX-LIST-NAME { in | out } [interface]
   distribute-list route-map ROUTE-MAP-NAME { in | out }
  exit-af-topology
```

**Direction matters critically:**

| Direction | Effect |
|-----------|--------|
| `out` | Filters routes before they are sent in EIGRP updates to neighbors |
| `in` | Filters routes as they are received from neighbors before installing in the topology table |

**Interface-specific vs global:**
- `out FastEthernet0/0` — applies only to updates sent out fa0/0
- `out` (no interface) — applies to all outbound updates
- `in FastEthernet0/0` — applies only to updates received on fa0/0

> **Exam tip:** A distribute-list `out` on router A prevents neighbor B from ever learning the filtered route. A distribute-list `in` on router B blocks the route from entering B's topology table. The same filtering goal can be achieved at either end — know which direction is being asked about on the exam.

### Route Maps

A route-map is an ordered list of policy clauses. Each clause has a sequence number, an action (permit or deny), optional `match` conditions, and optional `set` actions. Routes are evaluated against clauses in sequence-number order:

- **Match + Permit**: Route passes through; any `set` actions modify it
- **Match + Deny**: Route is blocked (dropped from the update)
- **No match**: Move to the next clause
- **End of route-map**: Implicit deny — no match at any clause = route dropped

```
route-map RM_NAME permit 10
 match ip address prefix-list PFX_NAME
 set tag 200
route-map RM_NAME permit 20
 ! no match = permit all remaining routes unmodified
```

> **Exam tip:** A route-map with a single `permit` clause and no `match` statement permits everything. A route-map with only a `deny` clause will drop everything that matches — plus everything else due to the implicit deny. Always end a route-map with `permit` + no match conditions unless you intend to block all unmatched routes.

### Route Tags

A route tag is a 32-bit integer that can be attached to any IP route. EIGRP (and other protocols) carry the tag transparently in their update messages. Tags are invisible to forwarding decisions — they exist purely as metadata for policy tools.

Tags are set with `set tag N` in a route-map and matched with `match tag N`. Their primary use case is **loop prevention in redistribution**: when routes are redistributed between routing domains, a tag marks them as "already redistributed." A distribute-list on the other side denies any routes carrying that tag, preventing them from being re-introduced into the domain of origin.

```
! R-A: tag routes entering from OSPF into EIGRP
route-map OSPF_INTO_EIGRP permit 10
 set tag 100

! R-B: block any EIGRP routes tagged 100 from going back into OSPF
route-map EIGRP_INTO_OSPF deny 10
 match tag 100
route-map EIGRP_INTO_OSPF permit 20
```

**Skills this lab develops:**

| Skill | Description |
|-------|-------------|
| Prefix-list construction | Deny specific prefixes; permit remainder with ge/le |
| Distribute-list direction | Apply in vs out; per-interface vs global |
| Named mode topology base | Correct sub-mode placement of distribute-list in EIGRP Named Mode |
| Route-map sequencing | Order permit/deny clauses; understand implicit deny |
| Route tag setting | Use set tag in a route-map applied to EIGRP updates |
| Tag-based filtering | Use match tag to block re-advertised or marked routes |
| Loop prevention | Understand how tags prevent routing loops in redistribution scenarios |

---

## 2. Topology & Scenario

As a lead network engineer at Acme Corp, you have received two change requests from the security and architecture teams:

**Change Request 1 (Security):** R4 hosts a quarantined edge segment (192.168.4.0/24). Branch A (R2) and Branch B (R3) must not have routing entries for this segment — traffic to the quarantined zone must flow exclusively through R1. Implement outbound filtering on R1 toward both branches, and inbound filtering on R3 as defense-in-depth.

**Change Request 2 (Architecture):** The network architecture team is planning future inter-protocol redistribution. As a preparatory step, Branch A's internal summary prefix (172.16.20.0/23) must be tagged with tag 200 as it leaves R2. The stub router R4 must drop any route carrying tag 200 to prevent a potential redistribution loop if OSPF is introduced later.

```
              ┌──────────────────────────────┐
              │             R1               │
              │        (Hub / Core)          │
              │    Lo0: 10.0.0.1/32          │
              │  [PFX_DENY_R4_STUB out Fa0/0]│
              │  [PFX_DENY_R4_STUB out Fa1/0]│
              └───────┬────────────┬─────────┘
           Fa0/0      │            │      Fa1/0
     10.12.0.1/30     │            │  10.13.0.1/30
                      │            │
     10.12.0.2/30     │            │  10.13.0.2/30
           Fa0/0      │            │      Fa0/0
     ┌────────────────┘            └──────────────────┐
     │                                                │
┌────┴──────────────────┐          ┌──────────────────┴────┐
│          R2           │          │          R3            │
│      (Branch A)       │          │       (Branch B)       │
│  Lo0: 10.0.0.2/32     │          │  Lo0: 10.0.0.3/32      │
│  Lo1: 172.16.20.1/24  │          │  Lo1: 172.16.30.1/24   │
│  Lo2: 172.16.21.1/24  │          │  Lo2: 172.16.31.1/24   │
│  [RM_TAG_BRANCH_A out]│          │  [PFX_DENY_R4_STUB in] │
└──────────┬────────────┘          └──────────────┬─────────┘
       Fa0/1│                                    Fa0/1│
  10.23.0.1/30│                              10.23.0.2/30│
              └────────────────────────────────────────┘
                              10.23.0.0/30
                                     │
              ┌──────────────────────────────┐
              │             R4               │
              │       (Stub / Edge)          │
              │  Lo0: 10.0.0.4/32            │
              │  Lo1: 192.168.4.1/24         │
              │  [RM_DENY_TAG_200 in]         │
              └──────────────────────────────┘
                  Fa0/0│ 10.14.0.2/30
                       │ (to R1 Fa1/1 10.14.0.1/30)
```

---

## 3. Hardware & Environment Specifications

**Platform:** GNS3 (Apple Silicon — Dynamips only)

### Router Hardware

| Device | Role | Platform | IOS Image | RAM |
|--------|------|----------|-----------|-----|
| R1 | Hub / Core | c7200 | c7200-adventerprisek9-mz.153-3.XB12.image | 512 MB |
| R2 | Branch A | c7200 | c7200-adventerprisek9-mz.153-3.XB12.image | 512 MB |
| R3 | Branch B | c7200 | c7200-adventerprisek9-mz.153-3.XB12.image | 512 MB |
| R4 | Stub / Edge | c7200 | c7200-adventerprisek9-mz.153-3.XB12.image | 512 MB |

### Adapter Cards

| Device | Slot | Adapter | Interfaces Used |
|--------|------|---------|----------------|
| R1 | 0 | C7200-IO-FE | fa0/0 → R2 |
| R1 | 1 | PA-2FE-TX | fa1/0 → R3; fa1/1 → R4 |
| R2 | 0 | C7200-IO-2FE | fa0/0 → R1; fa0/1 → R3 |
| R3 | 0 | C7200-IO-2FE | fa0/0 → R1; fa0/1 → R2 |
| R4 | 0 | C7200-IO-FE | fa0/0 → R1 |

### Cabling Table

| Link | Source | Destination | Subnet |
|------|--------|-------------|--------|
| L1 | R1 Fa0/0 | R2 Fa0/0 | 10.12.0.0/30 |
| L2 | R1 Fa1/0 | R3 Fa0/0 | 10.13.0.0/30 |
| L3 | R2 Fa0/1 | R3 Fa0/1 | 10.23.0.0/30 |
| L4 | R1 Fa1/1 | R4 Fa0/0 | 10.14.0.0/30 |

### Console Access Table

| Device | Console Port | Connection |
|--------|-------------|------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |
| R4 | 5004 | `telnet 127.0.0.1 5004` |

---

## 4. Base Configuration

Run `python3 setup_lab.py` to load the initial-configs. These are carried forward from Lab 06 solutions — all of the following are **already pre-configured:**

- IP addressing on all interfaces (including R4 Lo1: 192.168.4.1/24)
- IPv6 unicast-routing and IPv6 addressing on all links
- EIGRP Named Mode (AS 100) with dual-stack address families on R1–R4
- R4 stub mode (`eigrp stub connected summary`)
- R2 and R3 loopback interfaces (Lo1, Lo2) and their summary-address configurations
- EIGRP metric tuning: `bandwidth 512 / delay 2000` on R1 Fa0/0, `variance 5` on R1

**NOT pre-configured (you configure these):**

- Prefix-lists for route filtering
- Route-map for route tagging
- Distribute-lists on any router
- EIGRP topology base sub-mode entries

---

## 5. Lab Challenge: Core Implementation

### Task 1: Filter R4's Quarantined Network from Branch A

- Create a named prefix-list that explicitly denies R4's stub LAN (192.168.4.0 /24) and permits all other prefixes.
- Apply this prefix-list as an outbound distribute-list on R1, targeting the interface toward Branch A (R2) only.
- The filter must operate within the EIGRP Named Mode address-family's topology base.

**Verification:** `show ip route` on R2 must not contain 192.168.4.0. `show ip route` on R1 must still show 192.168.4.0 (R1's own routing table is unaffected by outbound filtering).

---

### Task 2: Apply Defense-in-Depth Filter on Branch B

- On R3, apply an inbound distribute-list on the interface facing R1 that uses the same prefix logic — deny 192.168.4.0/24, permit everything else.
- This ensures R3 independently enforces the policy, even if R1's outbound filter is misconfigured or bypassed.

**Verification:** `show ip route` on R3 must not contain 192.168.4.0. Confirm R3's other EIGRP routes (10.0.0.x/32 loopbacks, transit subnets) remain intact.

---

### Task 3: Tag Branch A's Summary Route for Loop Prevention

- On R2, create a prefix-list matching exactly the 172.16.20.0/23 summary prefix.
- Create a route-map with two sequences: sequence 10 matches that prefix-list and sets tag 200; sequence 20 permits all remaining routes without modification.
- Apply this route-map as an outbound distribute-list on R2 (apply to all outbound EIGRP updates, not interface-specific).

**Verification:** On R1 and R4, run `show ip eigrp topology 172.16.20.0/23`. The route entry must show `Tag: 200`. Other routes from R2 must carry no tag.

---

### Task 4: Block Tagged Routes on R4

- On R4, create a route-map with sequence 10 that denies any route carrying tag 200, and sequence 20 that permits all other routes.
- Apply this route-map as an inbound distribute-list on R4 (all inbound EIGRP updates).
- R4's `eigrp stub` already limits the routes it receives, but this tag filter adds explicit policy control.

**Verification:** `show ip route` on R4 must not contain 172.16.20.0/23. Run `show ip eigrp topology all-links` on R4 — the summary prefix should not appear in the topology table.

---

## 6. Verification & Analysis

### Task 1 — R1 Outbound Filter toward R2

```
R2# show ip route
     10.0.0.0/32 is subnetted, 4 subnets
D       10.0.0.1 [90/130816] via 10.12.0.1, 00:01:05, FastEthernet0/0
D       10.0.0.3 [90/156160] via 10.12.0.1, 00:01:05, FastEthernet0/0   ! ← R3 loopback still reachable via R1
D       10.0.0.4 [90/281856] via 10.12.0.1, 00:01:05, FastEthernet0/0   ! ← R4 Lo0 still reachable (not filtered)
     192.168.4.0/24 — NOT present in routing table                        ! ← quarantined prefix absent ✓

R1# show ip route 192.168.4.0
Routing entry for 192.168.4.0/24
  Known via "eigrp 100", distance 90, metric ...
  Last update from 10.14.0.2 on FastEthernet1/1                          ! ← R1 still sees it ✓
```

### Task 2 — R3 Inbound Filter on Fa0/0

```
R3# show ip route
     192.168.4.0/24 — NOT present in routing table                        ! ← inbound filter working ✓
     10.0.0.0/32 is subnetted, 4 subnets
D       10.0.0.1 [90/130816] via 10.13.0.1, 00:01:20, FastEthernet0/0   ! ← R1 Lo0 still present ✓
D       10.0.0.2 [90/156160] via 10.13.0.1, 00:01:20, FastEthernet0/0   ! ← R2 Lo0 still present ✓
D       10.0.0.4 [90/281856] via 10.13.0.1, 00:01:20, FastEthernet0/0   ! ← R4 Lo0 still present ✓

R3# show ip prefix-list PFX_DENY_R4_STUB
ip prefix-list PFX_DENY_R4_STUB: 2 entries
   seq 5 deny 192.168.4.0/24
   seq 10 permit 0.0.0.0/0 le 32
```

### Task 3 — Route Tag on R2's Summary

```
R1# show ip eigrp topology 172.16.20.0/23
EIGRP-IPv4 Topology Entry for AS(100)/ID(10.0.0.1) for 172.16.20.0/23
  State is Passive, Query origin flag is 1, 1 Successor(s), FD is 156160
  Routing Descriptor Blocks:
  10.12.0.2 (FastEthernet0/0), from 10.12.0.2, Send flag is 0x0
      Composite metric is (156160/128256), route is Internal
      Vector metric: ...
      Tag: 200                                                            ! ← tag 200 visible ✓
      External data: ...

R2# show route-map RM_TAG_BRANCH_A
route-map RM_TAG_BRANCH_A, permit, sequence 10
  Match clauses:
    ip address prefix-lists: PFX_BRANCH_A_SUMMARY
  Set clauses:
    tag 200                                                               ! ← set action confirmed ✓
  Policy routing matches: 0 packets, 0 bytes
route-map RM_TAG_BRANCH_A, permit, sequence 20
  Match clauses:
  Set clauses:
  Policy routing matches: 0 packets, 0 bytes
```

### Task 4 — R4 Tag-Based Inbound Filter

```
R4# show ip route 172.16.20.0
% Network not in table                                                   ! ← tagged route blocked ✓

R4# show ip eigrp topology all-links
EIGRP-IPv4 Topology Table for AS(100)/ID(10.0.0.4)
...
(172.16.20.0/23 does not appear)                                         ! ← absent from topology ✓

R4# show route-map RM_DENY_TAG_200
route-map RM_DENY_TAG_200, deny, sequence 10
  Match clauses:
    tag: 200                                                             ! ← deny clause active ✓
route-map RM_DENY_TAG_200, permit, sequence 20
```

---

## 7. Verification Cheatsheet

### Prefix-List Configuration

```
ip prefix-list NAME seq 5 deny NETWORK/LEN
ip prefix-list NAME seq 10 permit 0.0.0.0/0 le 32
```

| Command | Purpose |
|---------|---------|
| `ip prefix-list NAME seq N deny NET/LEN` | Deny specific prefix |
| `ip prefix-list NAME seq N permit 0.0.0.0/0 le 32` | Permit all remaining prefixes |
| `no ip prefix-list NAME` | Delete entire prefix-list |
| `show ip prefix-list NAME` | Display entries and hit counts |

> **Exam tip:** Every prefix-list ends with an implicit deny. Always add a `permit 0.0.0.0/0 le 32` as the last entry unless your intent is to block everything not explicitly permitted.

### EIGRP Named Mode Distribute-List (topology base)

```
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  topology base
   distribute-list prefix NAME { in | out } [interface]
   distribute-list route-map NAME { in | out }
  exit-af-topology
```

| Command | Purpose |
|---------|---------|
| `distribute-list prefix NAME out fa0/0` | Filter outbound updates on fa0/0 |
| `distribute-list prefix NAME in fa0/0` | Filter inbound updates received on fa0/0 |
| `distribute-list route-map NAME out` | Apply route-map to all outbound updates |
| `distribute-list route-map NAME in` | Apply route-map to all inbound updates |

> **Exam tip:** Distribute-list changes take effect immediately but only on future updates. After applying, clear EIGRP or wait for the next update cycle. `clear ip eigrp neighbors` forces an immediate reconvergence.

### Route-Map Configuration

```
route-map NAME permit|deny SEQUENCE
 match ip address prefix-list PFXLIST-NAME
 match tag TAG-VALUE
 set tag TAG-VALUE
```

| Command | Purpose |
|---------|---------|
| `route-map NAME permit N` | Permit clause — routes that match pass through |
| `route-map NAME deny N` | Deny clause — routes that match are dropped |
| `match ip address prefix-list NAME` | Match specific prefixes |
| `match tag N` | Match routes carrying a specific tag value |
| `set tag N` | Stamp matching routes with a tag |
| `show route-map NAME` | Display clauses and policy match counters |

### Verification Commands

| Command | What to Look For |
|---------|-----------------|
| `show ip route` | Confirm filtered prefix is absent |
| `show ip eigrp topology PREFIX/LEN` | Confirm tag value on specific route |
| `show ip eigrp topology all-links` | Full topology including non-successor paths |
| `show ip prefix-list NAME` | Entries + hit counts per sequence |
| `show route-map NAME` | Clauses + policy match counters |
| `show ip protocols` | Confirm distribute-list is registered |

### Wildcard / Prefix-List Mask Quick Reference

| Subnet Mask | Wildcard | Prefix-List Length |
|-------------|----------|--------------------|
| 255.255.255.0 | 0.0.0.255 | /24 |
| 255.255.254.0 | 0.0.1.255 | /23 |
| 255.255.252.0 | 0.0.3.255 | /22 |
| 255.255.0.0 | 0.0.255.255 | /16 |
| 0.0.0.0 | 255.255.255.255 | /0 (any) |

### Common EIGRP Filtering Failure Causes

| Symptom | Likely Cause |
|---------|-------------|
| Filtered route still appears in neighbor's table | Distribute-list applied `in` on wrong router instead of `out` on source router |
| All EIGRP routes disappear after applying filter | Missing `permit 0.0.0.0/0 le 32` — implicit deny blocking everything |
| Tag not visible in `show ip eigrp topology` | Route-map not applied as distribute-list, or permit 20 matching before set tag fires |
| Tag filter not blocking routes | Route-map sequence: permit clause with lower seq number matches before the deny |
| `distribute-list` command rejected | Entered at wrong hierarchy level — must be under `topology base` in Named Mode |

---

## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these solutions first!

### Task 1: Filter R4's Quarantined Network from Branch A

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1 — prefix-list + outbound distribute-list toward R2
ip prefix-list PFX_DENY_R4_STUB seq 5 deny 192.168.4.0/24
ip prefix-list PFX_DENY_R4_STUB seq 10 permit 0.0.0.0/0 le 32

router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  topology base
   distribute-list prefix PFX_DENY_R4_STUB out FastEthernet0/0
  exit-af-topology
 exit-address-family
```

</details>

<details>
<summary>Click to view Verification</summary>

```bash
R2# show ip route 192.168.4.0
% Network not in table

R1# show ip route 192.168.4.0
Routing entry for 192.168.4.0/24
  Known via "eigrp 100"...   ! R1 still knows it — only update to R2 is filtered
```

</details>

---

### Task 2: Apply Defense-in-Depth Filter on Branch B

<details>
<summary>Click to view R3 Configuration</summary>

```bash
! R3 — same prefix-list, inbound distribute-list on fa0/0 (from R1)
ip prefix-list PFX_DENY_R4_STUB seq 5 deny 192.168.4.0/24
ip prefix-list PFX_DENY_R4_STUB seq 10 permit 0.0.0.0/0 le 32

router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  topology base
   distribute-list prefix PFX_DENY_R4_STUB in FastEthernet0/0
  exit-af-topology
 exit-address-family
```

</details>

<details>
<summary>Click to view Verification</summary>

```bash
R3# show ip route 192.168.4.0
% Network not in table

R3# show ip prefix-list PFX_DENY_R4_STUB
ip prefix-list PFX_DENY_R4_STUB: 2 entries
   seq 5 deny 192.168.4.0/24    ! hit count increments each update cycle
   seq 10 permit 0.0.0.0/0 le 32
```

</details>

---

### Task 3: Tag Branch A's Summary Route

<details>
<summary>Click to view R2 Configuration</summary>

```bash
! R2 — prefix-list + route-map to tag summary + outbound distribute-list
ip prefix-list PFX_BRANCH_A_SUMMARY seq 5 permit 172.16.20.0/23

route-map RM_TAG_BRANCH_A permit 10
 match ip address prefix-list PFX_BRANCH_A_SUMMARY
 set tag 200
route-map RM_TAG_BRANCH_A permit 20

router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  topology base
   distribute-list route-map RM_TAG_BRANCH_A out
  exit-af-topology
 exit-address-family
```

</details>

<details>
<summary>Click to view Verification</summary>

```bash
R1# show ip eigrp topology 172.16.20.0/23
  ...
  Tag: 200   ! ← tag set on outgoing update from R2

R2# show route-map RM_TAG_BRANCH_A
route-map RM_TAG_BRANCH_A, permit, sequence 10
  Match clauses:
    ip address prefix-lists: PFX_BRANCH_A_SUMMARY
  Set clauses:
    tag 200
```

</details>

---

### Task 4: Block Tagged Routes on R4

<details>
<summary>Click to view R4 Configuration</summary>

```bash
! R4 — route-map to deny tag 200 + inbound distribute-list
route-map RM_DENY_TAG_200 deny 10
 match tag 200
route-map RM_DENY_TAG_200 permit 20

router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  topology base
   distribute-list route-map RM_DENY_TAG_200 in
  exit-af-topology
 exit-address-family
```

</details>

<details>
<summary>Click to view Verification</summary>

```bash
R4# show ip route 172.16.20.0
% Network not in table

R4# show route-map RM_DENY_TAG_200
route-map RM_DENY_TAG_200, deny, sequence 10
  Match clauses:
    tag: 200
route-map RM_DENY_TAG_200, permit, sequence 20
```

</details>

---

## 9. Troubleshooting Scenarios

Each ticket simulates a real-world fault. Inject the fault first, then diagnose and fix using only `show` commands.

### Workflow

```bash
python3 setup_lab.py                                   # reset to known-good state
python3 scripts/fault-injection/inject_scenario_01.py  # Ticket 1
python3 scripts/fault-injection/apply_solution.py      # restore after each ticket
```

---

### Ticket 1 — Branch-A Loopbacks Vanish from R1 and Downstream Routers

The Branch A team reports that their internal networks (172.16.20.x, 172.16.21.x) have disappeared from routing tables on R1, R3, and R4. R2 shows them as locally connected. No changes were made to R2 itself.

**Inject:** `python3 scripts/fault-injection/inject_scenario_01.py`

**Success criteria:** R1, R3, and R4 show 172.16.20.0/23 and 10.0.0.2/32 in their routing tables. `ping 172.16.20.1 source loopback0` succeeds from R1.

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Step 1: Confirm the symptom
R1# show ip route 172.16.20.0
% Network not in table

! Step 2: Check EIGRP neighbors — is R2 still adjacent?
R1# show ip eigrp neighbors
! R2 (10.12.0.2) should still appear — adjacency is fine

! Step 3: Check topology table on R1
R1# show ip eigrp topology all-links
! 172.16.20.0/23 and 10.0.0.2/32 are absent — R1 is not receiving them from R2

! Step 4: Check distribute-list configuration on R1
R1# show ip protocols
! Look for: Outgoing update filter list for all interfaces is...
! Or: Incoming update filter list...

! Step 5: Identify the fault
! The distribute-list PFX_DENY_R4_STUB is applied INBOUND on R1 Fa0/0
! The prefix-list denies 192.168.4.0/24 but passes everything else
! Wait — inbound means R1 is filtering routes coming FROM R2
! But R2's updates don't include 192.168.4.0/24 (that's R4's route)
! Actually: check if the prefix-list itself is the fault
! Perhaps the prefix-list was changed to deny 172.16.0.0/16 le 24?

R1# show ip prefix-list PFX_DENY_R4_STUB
! Fault: seq 5 deny 172.16.0.0/16 le 24 — wrong prefix, blocking R2's networks

! Alternative diagnosis: distribute-list direction changed to IN
R1# show running-config | section router eigrp
! Look for: distribute-list prefix PFX_DENY_R4_STUB IN FastEthernet0/0
! This would filter R2's inbound updates — blocking R2's routes from R1's topology table
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! The fault: distribute-list applied IN on R1 Fa0/0 (filtering R2's inbound updates)
! Fix: remove the inbound filter, restore the correct outbound filter

R1(config)# router eigrp ENARSI
R1(config-router)# address-family ipv4 unicast autonomous-system 100
R1(config-router-af)# topology base
R1(config-router-af-topology)# no distribute-list prefix PFX_DENY_R4_STUB in FastEthernet0/0
R1(config-router-af-topology)# distribute-list prefix PFX_DENY_R4_STUB out FastEthernet0/0
R1(config-router-af-topology)# exit-af-topology

! Verify recovery
R1# show ip route 172.16.20.0
D    172.16.20.0/23 [90/156160] via 10.12.0.2   ! ← R2's summary restored
R2# show ip route 192.168.4.0
% Network not in table                            ! ← quarantine filter still working
```

</details>

---

### Ticket 2 — R4 is Receiving Routes it Should Not Have Access To

The architecture team flags that R4 now has 172.16.20.0/23 in its routing table — a route that should be blocked by the tag-200 filter. The `eigrp stub` configuration on R4 is intact.

**Inject:** `python3 scripts/fault-injection/inject_scenario_02.py`

**Success criteria:** `show ip route` on R4 does not contain 172.16.20.0/23. `show route-map RM_DENY_TAG_200` shows the deny clause at a lower sequence number than any permit.

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Step 1: Confirm the symptom
R4# show ip route 172.16.20.0
D    172.16.20.0/23 [90/...]   ! ← present — fault confirmed

! Step 2: Verify distribute-list is still applied
R4# show ip protocols
! Look for: Incoming update filter list...

! Step 3: Inspect the route-map
R4# show route-map RM_DENY_TAG_200
route-map RM_DENY_TAG_200, permit, sequence 5    ! ← fault: permit 5 matches all routes first
  Match clauses:                                 !    no match conditions = matches everything
  Set clauses:
route-map RM_DENY_TAG_200, deny, sequence 10    ! ← deny 10 is never reached
  Match clauses:
    tag: 200

! Root cause: A permit clause with no match conditions at seq 5 was inserted
! It matches all routes before the deny 10 can evaluate tag 200
! This is the route-map sequence logic error — the permit takes precedence
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! Remove the spurious permit 5 sequence
R4(config)# no route-map RM_DENY_TAG_200 permit 5

! Verify the corrected route-map
R4# show route-map RM_DENY_TAG_200
route-map RM_DENY_TAG_200, deny, sequence 10    ! ← deny evaluated first ✓
  Match clauses:
    tag: 200
route-map RM_DENY_TAG_200, permit, sequence 20  ! ← catch-all permit ✓

! Verify R4 no longer receives the tagged route
R4# show ip route 172.16.20.0
% Network not in table   ! ← tag filter working ✓
```

</details>

---

### Ticket 3 — Branch B Has Lost All EIGRP Routes from Core

R3 has completely lost EIGRP-learned routes from R1, including infrastructure subnets and R4's loopback. R3's directly connected interfaces are up. EIGRP neighbors are still forming with R1 and R2.

**Inject:** `python3 scripts/fault-injection/inject_scenario_03.py`

**Success criteria:** R3's routing table shows all EIGRP-learned routes from R1 including 10.0.0.1/32, 10.0.0.4/32, and transit subnets. `show ip prefix-list PFX_DENY_R4_STUB` shows both seq 5 and seq 10.

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Step 1: Confirm R3's routing table
R3# show ip route eigrp
! No EIGRP routes from R1 — even 10.0.0.1/32 is missing

! Step 2: EIGRP neighbors still up?
R3# show ip eigrp neighbors
! R1 (10.13.0.1 via Fa0/0) present — adjacency fine

! Step 3: Check topology table — routes received at EIGRP level?
R3# show ip eigrp topology all-links
! Routes from R1 absent from topology table entirely
! → The inbound distribute-list is blocking them before they enter the topology table

! Step 4: Inspect the prefix-list
R3# show ip prefix-list PFX_DENY_R4_STUB
ip prefix-list PFX_DENY_R4_STUB: 1 entries
   seq 5 deny 192.168.4.0/24
   ! seq 10 permit 0.0.0.0/0 le 32 — MISSING

! Root cause: The permit catch-all (seq 10) was removed
! The implicit deny at the end of the prefix-list now blocks ALL routes not matching seq 5
! Since 192.168.4.0/24 is already blocked by seq 5, everything else hits the implicit deny
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! Restore the permit catch-all to the prefix-list
R3(config)# ip prefix-list PFX_DENY_R4_STUB seq 10 permit 0.0.0.0/0 le 32

! Verify the prefix-list is complete
R3# show ip prefix-list PFX_DENY_R4_STUB
ip prefix-list PFX_DENY_R4_STUB: 2 entries
   seq 5 deny 192.168.4.0/24
   seq 10 permit 0.0.0.0/0 le 32   ! ← catch-all restored ✓

! Wait a few seconds for EIGRP to re-advertise, then verify
R3# show ip route eigrp
D    10.0.0.1/32 [90/130816] via 10.13.0.1   ! ← R1 loopback restored ✓
D    10.0.0.4/32 [90/...] via 10.13.0.1      ! ← R4 loopback restored ✓
R3# show ip route 192.168.4.0
% Network not in table                        ! ← quarantine still enforced ✓
```

</details>

---

## 10. Lab Completion Checklist

### Core Implementation

- [ ] **Task 1:** Prefix-list `PFX_DENY_R4_STUB` created on R1 with deny 192.168.4.0/24 and permit 0.0.0.0/0 le 32
- [ ] **Task 1:** Distribute-list applied outbound on R1 Fa0/0 under EIGRP topology base
- [ ] **Task 1:** `show ip route` on R2 confirms 192.168.4.0/24 absent; R1's own table retains it
- [ ] **Task 2:** Same prefix-list created on R3; distribute-list applied inbound on R3 Fa0/0
- [ ] **Task 2:** `show ip route` on R3 confirms 192.168.4.0/24 absent; all other routes intact
- [ ] **Task 3:** Prefix-list `PFX_BRANCH_A_SUMMARY` on R2 matching 172.16.20.0/23
- [ ] **Task 3:** Route-map `RM_TAG_BRANCH_A` with seq 10 (set tag 200) and seq 20 (permit all)
- [ ] **Task 3:** Distribute-list route-map applied outbound on R2 under topology base
- [ ] **Task 3:** `show ip eigrp topology 172.16.20.0/23` on R1 shows Tag: 200
- [ ] **Task 4:** Route-map `RM_DENY_TAG_200` on R4 with seq 10 (deny tag 200) and seq 20 (permit all)
- [ ] **Task 4:** Distribute-list route-map applied inbound on R4 under topology base
- [ ] **Task 4:** `show ip route` on R4 confirms 172.16.20.0/23 absent

### Troubleshooting

- [ ] **Ticket 1:** Identified distribute-list applied in wrong direction; restored correct outbound filter
- [ ] **Ticket 2:** Identified spurious low-sequence permit clause bypassing the tag deny; removed it
- [ ] **Ticket 3:** Identified missing permit catch-all causing implicit deny to block all routes; restored seq 10
