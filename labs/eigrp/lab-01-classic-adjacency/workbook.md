# Lab 01 — EIGRP Classic Mode: Neighbor Adjacency & Basic IPv4

**Chapter:** EIGRP | **Exam:** 300-410 ENARSI | **Blueprint:** 1.9.b
**Difficulty:** Foundation | **Estimated Time:** 60 minutes

---

## Section 1 — Concepts

### EIGRP Overview

Enhanced Interior Gateway Routing Protocol (EIGRP) is Cisco's advanced distance-vector routing protocol. It uses the Diffusing Update Algorithm (DUAL) to guarantee loop-free path selection and fast convergence without periodic full-table updates.

Key characteristics:
- **Transport:** IP protocol number 88 (not TCP or UDP)
- **Multicast group:** 224.0.0.10 (all EIGRP routers)
- **Administrative Distance:** 90 internal, 170 external
- **Composite metric:** Calculated from bandwidth, delay, reliability, load, and MTU (K-values K1–K5)
- **Default K-values:** K1=1, K2=0, K3=1, K4=0, K5=0 (bandwidth + delay only)

### Classic Mode

In classic (traditional) mode, EIGRP is configured with a single global process under `router eigrp <AS>`. Classic mode supports IPv4 only by default. Named mode (IOS 15.0+) extends this with explicit address-family blocks — covered in Lab 02.

```
router eigrp <AS-number>
 network <address> <wildcard-mask>
 no auto-summary
```

### Neighbor Adjacency Requirements

Two EIGRP routers form an adjacency (neighbor relationship) when **all** of the following match:

| Requirement | Notes |
|-------------|-------|
| Autonomous System number | Must be identical on both sides |
| K-values (metric weights) | Must be identical; mismatch = no adjacency |
| Authentication | Must match if configured |
| Common subnet | Interfaces must share the same IP subnet |

Adjacencies are established via Hello packets. A router is declared down if no Hello is received within the **Hold Time** (default: 15 sec = 3 × Hello interval of 5 sec).

### The `network` Command

```
network <network-address> <wildcard-mask>
```

The wildcard mask is the bitwise inverse of the subnet mask. EIGRP activates on any interface whose IP address falls within the specified range — it does **not** create a route to that network. Only add `network` statements for subnets reachable via **this router's own interfaces**.

### Automatic Summarization

By default, IOS performs classful auto-summarization at major network boundaries. Always configure `no auto-summary` in modern networks to prevent unexpected summarization.

---

## Section 2 — Topology

### Network Diagram

```
                     ┌──────────────────────────────┐
                     │             R1               │
                     │      Lo0: 10.0.0.1/32        │
                     │      Hub / Core              │
                     │      c7200 | IOS 15.3(3)XB12 │
                     └──────┬───────────────┬───────┘
                        fa0/0             fa1/0
                     10.12.0.1         10.13.0.1
                            │               │
          ┌─────────────────┘               └────────────────────┐
          │ 10.12.0.0/30                         10.13.0.0/30    │
          │                                                       │
┌─────────┴─────────────────┐         ┌──────────────────────────┴────┐
│           R2              │         │              R3               │
│   Lo0: 10.0.0.2/32        │         │   Lo0: 10.0.0.3/32            │
│   Branch A                │         │   Branch B                    │
│   c7200 | IOS 15.3(3)XB12 │         │   c7200 | IOS 15.3(3)XB12    │
└─────────────┬─────────────┘         └──────────────┬────────────────┘
           fa0/1                                   fa0/1
        10.23.0.1                               10.23.0.2
                 └─────────── 10.23.0.0/30 ──────────┘
```

### Cabling Table

| Link ID | Source | Source Interface | Destination | Destination Interface | Subnet IPv4 |
|---------|--------|------------------|-------------|----------------------|-------------|
| L1 | R1 | fa0/0 | R2 | fa0/0 | 10.12.0.0/30 |
| L2 | R1 | fa1/0 | R3 | fa0/0 | 10.13.0.0/30 |
| L3 | R2 | fa0/1 | R3 | fa0/1 | 10.23.0.0/30 |

### Console Access Table

| Router | Role | Console (Telnet) | Loopback0 |
|--------|------|-----------------|-----------|
| R1 | Hub / Core | 127.0.0.1:5001 | 10.0.0.1/32 |
| R2 | Branch A | 127.0.0.1:5002 | 10.0.0.2/32 |
| R3 | Branch B | 127.0.0.1:5003 | 10.0.0.3/32 |

---

## Section 3 — Hardware

### Platform Specifications

All routers use **Cisco 7200 (c7200)** with **IOS 15.3(3)XB12** (`c7200-adventerprisek9-mz.153-3.XB12.image`).

| Router | Slot 0 | Slot 1 | Active Interfaces |
|--------|--------|--------|-------------------|
| R1 | C7200-IO-FE → fa0/0 | PA-2FE-TX → fa1/0, fa1/1 | fa0/0, fa1/0, Lo0 |
| R2 | C7200-IO-2FE → fa0/0, fa0/1 | — | fa0/0, fa0/1, Lo0 |
| R3 | C7200-IO-2FE → fa0/0, fa0/1 | — | fa0/0, fa0/1, Lo0 |

> **Note:** R1 fa1/1 is reserved for R4 (introduced in Lab 06). Do not configure it in this lab.

### GNS3 Notes

- Allocate 256 MB DRAM per c7200 instance
- Set an Idle-PC value on each router to prevent CPU saturation
- Connect console via Telnet: GNS3 assigns ports starting at the base configured per project (R1=5001, R2=5002, R3=5003)

---

## Section 4 — Base Configuration

The `initial-configs/` directory contains pre-loaded configurations. Push them to routers using:

```bash
python3 setup_lab.py
```

**Pre-loaded (do not reconfigure):**
- Hostnames (R1, R2, R3)
- `no ip domain-lookup`
- All interface IP addresses and descriptions
- `no shutdown` on active interfaces

**NOT pre-loaded — this is your task:**
- EIGRP routing process
- Subnet advertisement
- Summarization behavior

---

## Section 5 — Challenge

### Scenario

> Acme Corp is deploying EIGRP across its enterprise WAN. As the lead network engineer, you are responsible for bringing up EIGRP classic mode (AS 100) on the three-router hub-and-spoke topology before a scheduled production cutover. IP addressing is already in place. Your task is to configure EIGRP adjacencies and verify full IPv4 reachability across all three routers.

### Task 1: EIGRP Classic Mode Activation

- Enable EIGRP in Autonomous System 100 on all three routers (R1, R2, and R3).

**Verification:** `show ip protocols` on each router must confirm EIGRP AS 100 is active with default K-values (K1=1, K2=0, K3=1, K4=0, K5=0).

---

### Task 2: Subnet Advertisement

- Advertise all subnets directly connected to each router into EIGRP.
- Each router must only advertise the subnets reachable via its own interfaces — do not advertise subnets belonging to links the router does not participate in.
- Disable classful automatic summarization on all three routers to prevent unintended route aggregation at major network boundaries.

**Verification:** `show ip eigrp topology` on each router must list all three point-to-point links and all loopback prefixes as known EIGRP routes.

---

### Task 3: Neighbor Adjacency Confirmation

- Confirm that EIGRP neighbor adjacencies form on all three links: R1↔R2 (L1), R1↔R3 (L2), and R2↔R3 (L3).

**Verification:** `show ip eigrp neighbors` on each router must show exactly two active neighbors with non-zero uptime.

---

### Task 4: End-to-End Loopback Reachability

- Verify that every Loopback0 address (10.0.0.1, 10.0.0.2, 10.0.0.3) is reachable from every other router.
- Source each ping from the sending router's own Loopback0.

**Verification:** All six Loopback0-to-Loopback0 pings must return 100% success (5/5).

---

## Section 6 — Verification

### Step-by-Step Verification Sequence

#### 1. Verify EIGRP Neighbor Table

```
R1# show ip eigrp neighbors
```

Expected — two neighbors, one per link:

```
EIGRP-IPv4 Neighbors for AS(100)
H   Address         Interface       Hold Uptime   SRTT   RTO  Q  Seq
                                    (sec)         (ms)       Cnt Num
1   10.13.0.2       Fa1/0             12 00:01:23    5   200  0   3
0   10.12.0.2       Fa0/0             14 00:01:45    5   200  0   5
```

Run `show ip eigrp neighbors` on R2 and R3 — each must show exactly two neighbors.

#### 2. Verify EIGRP Routes in the Routing Table

```
R1# show ip route eigrp
```

Expected — R1 learns remote loopbacks and the R2–R3 link:

```
      10.0.0.0/8 is variably subnetted, 5 subnets, 2 masks
D        10.0.0.2/32 [90/130816] via 10.12.0.2, 00:01:30, FastEthernet0/0
D        10.0.0.3/32 [90/130816] via 10.13.0.2, 00:01:30, FastEthernet1/0
      10.23.0.0/30 is subnetted, 1 subnet
D        10.23.0.0 [90/30720] via 10.12.0.2, 00:01:30, FastEthernet0/0
                   [90/30720] via 10.13.0.2, 00:01:30, FastEthernet1/0
```

#### 3. Verify End-to-End Reachability

```
R1# ping 10.0.0.2 source Loopback0
R1# ping 10.0.0.3 source Loopback0
R2# ping 10.0.0.1 source Loopback0
R2# ping 10.0.0.3 source Loopback0
R3# ping 10.0.0.1 source Loopback0
R3# ping 10.0.0.2 source Loopback0
```

All six pings must return `!!!!!` (100% success).

#### 4. Verify EIGRP Topology Table

```
R1# show ip eigrp topology
```

Confirm successors are present for all remote prefixes. Equal-cost paths (e.g., 10.23.0.0/30 via both R2 and R3) appear as two entries under the same prefix.

#### 5. Verify EIGRP Process Summary

```
R1# show ip protocols
```

Confirm: Routing Protocol = eigrp 100, K-values match defaults (K1=1 K2=0 K3=1 K4=0 K5=0), and all expected networks appear under "Routing for Networks".

---

## Section 7 — Cheatsheet

### EIGRP Process Configuration

```
router eigrp <AS>
 network <address> <wildcard>
 no auto-summary
 eigrp log-neighbor-changes
```

| Command | Purpose |
|---------|---------|
| `router eigrp <AS>` | Start an EIGRP classic mode process with the given AS number |
| `network <address> <wildcard>` | Activate EIGRP on any interface whose IP falls within the range |
| `no auto-summary` | Disable classful summarization at major network boundaries |
| `eigrp log-neighbor-changes` | Log adjacency up/down events to the console and syslog |

### Interface Controls

```
router eigrp <AS>
 passive-interface <interface>
 no passive-interface <interface>
```

| Command | Purpose |
|---------|---------|
| `passive-interface <interface>` | Suppress outbound Hello packets — network is advertised but adjacency cannot form |
| `no passive-interface <interface>` | Re-enable Hello packets; adjacency can form |

> **Exam tip:** `passive-interface` is the most common cause of a one-sided "missing neighbor" fault. The passive router still advertises the subnet but never sends Hellos.

### Verification Commands

| Command | What to Look For |
|---------|-----------------|
| `show ip eigrp neighbors` | Each active neighbor, interface, hold timer, uptime |
| `show ip eigrp topology` | Successors and Feasible Successors with FD and RD values |
| `show ip eigrp topology all-links` | All known paths, including those that fail the Feasibility Condition |
| `show ip route eigrp` | Routes installed in the RIB — look for `D` prefix and `[90/…]` AD/metric |
| `show ip protocols` | EIGRP AS number, K-values, networks being advertised, neighbors |
| `debug eigrp packets` | Real-time Hello, Update, ACK, and Query packet flow |
| `debug ip eigrp` | DUAL computation and route change events |

### Wildcard Mask Quick Reference

| Subnet Mask | Wildcard Mask | Common Use |
|-------------|---------------|------------|
| /30 (255.255.255.252) | 0.0.0.3 | Point-to-point WAN links |
| /24 (255.255.255.0) | 0.0.0.255 | Standard LAN segments |
| /32 (255.255.255.255) | 0.0.0.0 | Loopback interfaces (exact match) |

### Common Adjacency Failure Causes

| Symptom | Likely Cause |
|---------|-------------|
| No neighbors at all | AS mismatch, K-value mismatch, `passive-interface` |
| One-sided adjacency | Firewall blocking 224.0.0.10, ACL on interface |
| Routes missing for a specific prefix | Missing `network` statement, `passive-interface` |
| Routes disappear then return | Hold timer expired — check Hello/Hold timers |

---

## Section 8 — Solutions

<details>
<summary>R1 — Complete Solution Configuration (click to expand)</summary>

```
!
hostname R1
!
no ip domain-lookup
!
interface Loopback0
 description Lo0 - Router ID
 ip address 10.0.0.1 255.255.255.255
!
interface FastEthernet0/0
 description Link to R2 fa0/0 -- 10.12.0.0/30
 ip address 10.12.0.1 255.255.255.252
 no shutdown
!
interface FastEthernet1/0
 description Link to R3 fa0/0 -- 10.13.0.0/30
 ip address 10.13.0.1 255.255.255.252
 no shutdown
!
router eigrp 100
 eigrp log-neighbor-changes
 network 10.12.0.0 0.0.0.3
 network 10.13.0.0 0.0.0.3
 network 10.0.0.1 0.0.0.0
 no auto-summary
!
end
```

**R1 network statements — interface verification:**
- `network 10.12.0.0 0.0.0.3` → matches fa0/0 (10.12.0.1) ✓
- `network 10.13.0.0 0.0.0.3` → matches fa1/0 (10.13.0.1) ✓
- `network 10.0.0.1 0.0.0.0` → matches Lo0 (10.0.0.1) ✓
- 10.23.0.0/30 is NOT on R1 → no network statement for it ✓

</details>

<details>
<summary>R2 — Complete Solution Configuration (click to expand)</summary>

```
!
hostname R2
!
no ip domain-lookup
!
interface Loopback0
 description Lo0 - Router ID
 ip address 10.0.0.2 255.255.255.255
!
interface FastEthernet0/0
 description Link to R1 fa0/0 -- 10.12.0.0/30
 ip address 10.12.0.2 255.255.255.252
 no shutdown
!
interface FastEthernet0/1
 description Link to R3 fa0/1 -- 10.23.0.0/30
 ip address 10.23.0.1 255.255.255.252
 no shutdown
!
router eigrp 100
 eigrp log-neighbor-changes
 network 10.12.0.0 0.0.0.3
 network 10.23.0.0 0.0.0.3
 network 10.0.0.2 0.0.0.0
 no auto-summary
!
end
```

**R2 network statements — interface verification:**
- `network 10.12.0.0 0.0.0.3` → matches fa0/0 (10.12.0.2) ✓
- `network 10.23.0.0 0.0.0.3` → matches fa0/1 (10.23.0.1) ✓
- `network 10.0.0.2 0.0.0.0` → matches Lo0 (10.0.0.2) ✓
- 10.13.0.0/30 is NOT on R2 → no network statement for it ✓

</details>

<details>
<summary>R3 — Complete Solution Configuration (click to expand)</summary>

```
!
hostname R3
!
no ip domain-lookup
!
interface Loopback0
 description Lo0 - Router ID
 ip address 10.0.0.3 255.255.255.255
!
interface FastEthernet0/0
 description Link to R1 fa1/0 -- 10.13.0.0/30
 ip address 10.13.0.2 255.255.255.252
 no shutdown
!
interface FastEthernet0/1
 description Link to R2 fa0/1 -- 10.23.0.0/30
 ip address 10.23.0.2 255.255.255.252
 no shutdown
!
router eigrp 100
 eigrp log-neighbor-changes
 network 10.13.0.0 0.0.0.3
 network 10.23.0.0 0.0.0.3
 network 10.0.0.3 0.0.0.0
 no auto-summary
!
end
```

**R3 network statements — interface verification:**
- `network 10.13.0.0 0.0.0.3` → matches fa0/0 (10.13.0.2) ✓
- `network 10.23.0.0 0.0.0.3` → matches fa0/1 (10.23.0.2) ✓
- `network 10.0.0.3 0.0.0.0` → matches Lo0 (10.0.0.3) ✓
- 10.12.0.0/30 is NOT on R3 → no network statement for it ✓

</details>

---

## Section 9 — Troubleshooting

> **Instructions:** Each ticket below describes observable symptoms only. Diagnose based on symptoms using the verification commands from Section 6. Do not read the fault script `README.md` before attempting — it reveals the injected fault.

### Ticket 09-1: Branch A Is Completely Isolated

**Reported by:** NOC
**Severity:** Critical
**Symptom:** R2 reports zero EIGRP neighbors. Pings from R2 to 10.0.0.1 (R1 loopback) and 10.0.0.3 (R3 loopback) fail. R1 and R3 appear to have a functioning adjacency with each other. The network team confirms EIGRP is configured on R2.

**To inject this fault:**
```bash
python3 scripts/fault-injection/inject_scenario_01.py
```

---

### Ticket 09-2: R1 Cannot Reach Branch A

**Reported by:** Operations
**Severity:** High
**Symptom:** `show ip eigrp neighbors` on R1 shows only one neighbor (R3). Pings from R1 to R2's loopback (10.0.0.2) fail. R2 and R3 have a working adjacency, but R2 cannot reach any R1 networks. A per-interface EIGRP setting on R1 is suspected.

**To inject this fault:**
```bash
python3 scripts/fault-injection/inject_scenario_02.py
```

---

### Ticket 09-3: R3 Loopback Unreachable

**Reported by:** Server Team
**Severity:** Medium
**Symptom:** All three EIGRP adjacencies are Up. R1 and R2 can successfully ping R3's physical interface addresses (10.13.0.2, 10.23.0.2). However, pings to R3's loopback (10.0.0.3) fail from both R1 and R2. R3 shows its own loopback as directly connected. The 10.0.0.3/32 prefix is absent from R1 and R2 routing tables.

**To inject this fault:**
```bash
python3 scripts/fault-injection/inject_scenario_03.py
```

---

## Section 10 — Completion Checklist

Work through each item. Mark complete only after running the relevant `show` command.

**EIGRP Adjacency**
- [ ] `show ip eigrp neighbors` on R1 — shows 2 neighbors (R2 on fa0/0, R3 on fa1/0)
- [ ] `show ip eigrp neighbors` on R2 — shows 2 neighbors (R1 on fa0/0, R3 on fa0/1)
- [ ] `show ip eigrp neighbors` on R3 — shows 2 neighbors (R1 on fa0/0, R2 on fa0/1)

**EIGRP Routing Table**
- [ ] `show ip route eigrp` on R1 — D routes for 10.0.0.2/32, 10.0.0.3/32, 10.23.0.0/30
- [ ] `show ip route eigrp` on R2 — D routes for 10.0.0.1/32, 10.0.0.3/32, 10.13.0.0/30
- [ ] `show ip route eigrp` on R3 — D routes for 10.0.0.1/32, 10.0.0.2/32, 10.12.0.0/30

**End-to-End Reachability**
- [ ] `ping 10.0.0.2 source Loopback0` from R1 — 5/5 success
- [ ] `ping 10.0.0.3 source Loopback0` from R1 — 5/5 success
- [ ] `ping 10.0.0.1 source Loopback0` from R2 — 5/5 success
- [ ] `ping 10.0.0.3 source Loopback0` from R2 — 5/5 success
- [ ] `ping 10.0.0.1 source Loopback0` from R3 — 5/5 success
- [ ] `ping 10.0.0.2 source Loopback0` from R3 — 5/5 success

**Configuration Quality**
- [ ] `show ip protocols` on all routers — K-values: K1=1 K2=0 K3=1 K4=0 K5=0
- [ ] `no auto-summary` confirmed in `router eigrp 100` on all routers
- [ ] `eigrp log-neighbor-changes` present on all routers

**Troubleshooting Tickets**
- [ ] Ticket 09-1 (Branch A Isolated) — diagnosed and resolved
- [ ] Ticket 09-2 (R1 Cannot Reach Branch A) — diagnosed and resolved
- [ ] Ticket 09-3 (R3 Loopback Unreachable) — diagnosed and resolved
