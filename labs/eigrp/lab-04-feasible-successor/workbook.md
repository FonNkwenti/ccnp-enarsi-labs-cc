# EIGRP Lab 04 — Loop-Free Path Selection: FD, RD, FC & Feasible Successors

**Exam:** CCNP ENARSI 300-410
**Difficulty:** Intermediate
**Estimated Time:** 90 minutes

---

## 1. Concepts & Skills Covered

### Blueprint Coverage

| Blueprint ID | Topic |
|---|---|
| 1.9.c | Loop-free path selection (RD, FD, FC, successor, feasible successor) |
| 1.9.e | Load balancing (equal-cost, unequal-cost with variance) |

### Key Concepts

**Feasible Distance (FD) and Reported Distance (RD)**

EIGRP calculates two critical metrics for loop-free routing:
- **Feasible Distance (FD):** The best metric to reach a destination from *this* router. The FD becomes the metric of the chosen Successor.
- **Reported Distance (RD):** The metric a neighbor reports for reaching a destination. When R1 hears from R2 "I can reach 10.0.0.3 with metric 20," that 20 is the RD from R1's perspective.

**The Feasibility Condition**

EIGRP prevents loops by requiring an alternative route (Feasible Successor) to meet this condition:
```
RD from that neighbor < FD of the current Successor
```

If a neighbor's RD exceeds the current FD, it cannot be a Feasible Successor — it may create a loop.

**Successor vs. Feasible Successor**

- **Successor:** The neighbor with the *best* (lowest) metric to a destination. Becomes the primary next-hop for that prefix.
- **Feasible Successor:** A backup neighbor whose RD is less than the current FD. Can be used immediately if the Successor fails, without triggering reconvergence (DUAL recomputation).

**Variance and Unequal-Cost Load Balancing**

By default, EIGRP only load-balances across paths with *equal* metrics. The `variance` multiplier allows unequal-cost paths to be used:
```
variance N
```
A path is usable if: `metric ≤ FD × variance`

For example, `variance 3` allows any path with metric ≤ FD × 3 to be a Successor. This enables faster links to share traffic with slower backup links.

---

## 2. Topology & Scenario

### Enterprise Scenario

Acme Corp has deployed EIGRP across its three-site network (Lab 01 baseline). You are now tasked with understanding how EIGRP chooses backup paths and handles link failures. By examining the Feasibility Condition and configuring variance, you will learn how EIGRP achieves sub-second convergence and loop-free alternate routing.

This lab continues from Lab 01 — all routers are running EIGRP classic mode, AS 100, with no auto-summary. You will now inspect the topology database to understand why certain paths are feasible and others are not.

### Topology Reference

The three-router triangle from Lab 01 continues:
- **R1** (Hub): 10.0.0.1/32, connects to R2 (10.12.0.0/30) and R3 (10.13.0.0/30)
- **R2** (Branch A): 10.0.0.2/32, connects to R1 and R3 (10.23.0.0/30)
- **R3** (Branch B): 10.0.0.3/32, connects to R1 and R2

> Open `topology.drawio` in Draw.io for the interactive diagram.

---

## 3. Hardware & Environment Specifications

### Device Platform Summary

| Device | Platform | Role | RAM | IOS Image |
|---|---|---|---|---|
| R1 | c7200 | Hub / Core | 512 MB | c7200-adventerprisek9-mz.153-3.XB12.image |
| R2 | c3725 | Branch A | 256 MB | c3725-adventerprisek9-mz.124-15.T14.image |
| R3 | c3725 | Branch B | 256 MB | c3725-adventerprisek9-mz.124-15.T14.image |

### IP Address Reference

| Device | Interface | IPv4 Address |
|---|---|---|
| R1 | Loopback0 | 10.0.0.1/32 |
| R1 | FastEthernet0/0 | 10.12.0.1/30 |
| R1 | FastEthernet1/0 | 10.13.0.1/30 |
| R2 | Loopback0 | 10.0.0.2/32 |
| R2 | FastEthernet0/0 | 10.12.0.2/30 |
| R2 | FastEthernet0/1 | 10.23.0.1/30 |
| R3 | Loopback0 | 10.0.0.3/32 |
| R3 | FastEthernet0/0 | 10.13.0.2/30 |
| R3 | FastEthernet0/1 | 10.23.0.2/30 |

### Cabling Table

| Link ID | Source | Interface | Target | Interface | Subnet |
|---|---|---|---|---|---|
| L1 | R1 | Fa0/0 | R2 | Fa0/0 | 10.12.0.0/30 |
| L2 | R1 | Fa1/0 | R3 | Fa0/0 | 10.13.0.0/30 |
| L3 | R2 | Fa0/1 | R3 | Fa0/1 | 10.23.0.0/30 |

### Console Access Table

| Device | Console Port | Connection Command |
|---|---|---|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |

---

## 4. Base Configuration

The initial configuration for Lab 04 is the **exact working solution from Lab 03** — all three routers are running EIGRP classic mode (AS 100) with proper neighbor adjacencies and routing in place. No changes to the base EIGRP configuration are needed; you will only inspect topology metrics and add variance for load balancing.

**Pre-configured (from Lab 03):**
- ✅ EIGRP AS 100 on all routers
- ✅ `no auto-summary` on all routers
- ✅ All neighbor adjacencies established
- ✅ Full IPv4 reachability

**Not configured (your task):**
- ❌ Variance for unequal-cost load balancing
- ❌ RD/FD analysis and interpretation

Verify the base state:
```
R1# show ip eigrp neighbors
R1# show ip eigrp topology
R1# show ip route eigrp
```

---

## 5. Lab Challenge: Core Implementation

> Complete each objective in order. Verify each before moving to the next.

### Objective 1 — Understand Feasible Distance and Reported Distance

Examine R1's EIGRP topology table for the route to R3's Loopback0 (10.0.0.3/32):

1. Run: `show ip eigrp topology 10.0.0.3/32`
2. Identify the **Feasible Distance (FD):** This is R1's best metric to 10.0.0.3
3. For each neighbor (R2 and R3), identify the **Reported Distance (RD):** What metric does each neighbor report for 10.0.0.3?
4. Note which neighbor is the **Successor** (lowest RD becomes the FD)
5. Identify any **Feasible Successors** — neighbors whose RD < current FD

**Record your findings:**
- FD for 10.0.0.3/32: `_______`
- RD via R2 (10.12.0.2): `_______` (Feasible Successor? Yes / No)
- RD via R3 (10.13.0.2): `_______` (Successor / Neither)

### Objective 2 — Verify the Feasibility Condition

For each route (10.0.0.2/32, 10.0.0.3/32, 10.23.0.0/30), verify that all Feasible Successors meet the Feasibility Condition:
```
RD (from backup neighbor) < FD (of current Successor)
```

Use `show ip eigrp topology all-links` to see all paths, including non-feasible ones.

**Record your findings:**
- Route 10.0.0.3/32: Current Successor FD = `_____`, Backup RD = `_____`, FC Met? Yes / No
- Route 10.23.0.0/30: Current Successor FD = `_____`, Backup RD = `_____`, FC Met? Yes / No

### Objective 3 — Simulate a Successor Failure and Observe Failover

1. Identify R1's current Successor for 10.0.0.3/32 (should be via R3 directly, with lower metric than via R2)
2. Shut down the interface from R1 that connects to that Successor: `shutdown` the interface
3. Watch the route immediately failover to the Feasible Successor — **no DUAL recalculation needed**
4. Run `show ip route eigrp | include 10.0.0.3` — the next-hop should now be via the former backup
5. Verify convergence time is sub-second (no "`q,u`" flags in the topology output)
6. Restore the interface: `no shutdown`

**Record your findings:**
- Original Successor via: `_________`
- Failover Successor via: `_________`
- Convergence time (immediate / sub-second / slow): `_________`

### Objective 4 — Configure Variance for Unequal-Cost Load Balancing

1. Examine the current metrics for 10.0.0.3/32 from R1:
   - Via R3 (direct): FD = `_____`
   - Via R2 (via R3 behind R2): RD = `_____`

2. Calculate the ratio: `RD / FD = _____`

3. Configure variance on R1 to allow unequal-cost load balancing:
   ```
   router eigrp 100
    variance 3
   ```

4. Run `show ip route eigrp` — the route 10.0.0.3/32 should now show **two next-hops** (both R2 and R3)

5. Verify with `show ip eigrp topology 10.0.0.3/32` — both paths should now be marked as Successors (not just one Successor + one Feasible Successor)

**Record your findings:**
- Variance configured: `_____`
- 10.0.0.3/32 now has how many next-hops? `_____`
- Load balancing active? Yes / No

### Objective 5 — Verify and Test Unequal-Cost Load Balancing

1. Check the routing table on R1 for 10.0.0.3:
   ```
   R1# show ip route 10.0.0.3
   ```
   Both next-hops should appear.

2. Send pings from R1 to 10.0.0.3 with source 10.0.0.1 and capture traffic to verify traffic is sent via both paths:
   ```
   R1# ping 10.0.0.3 source 10.0.0.1 repeat 10
   ```

3. Check interface stats on R1 to verify packets are being sent via both Fa0/0 (toward R2) and Fa1/0 (toward R3):
   ```
   R1# show ip interface Fa0/0
   R1# show ip interface Fa1/0
   ```

---

## 6. Verification & Analysis

### After Objective 1–2: Topology Inspection

**Check FD/RD values:**
```
R1# show ip eigrp topology 10.0.0.3/32
```

Expected output format:
```
P 10.0.0.3/32, 1 successors, FD is 30720, serno 6
        via 10.13.0.2 (30720/20480), Serial1
        via 10.12.0.2 (33280/30720), Serial0
```

Interpretation:
- **P:** Passive (stable) — no DUAL computation in progress
- **1 successors:** Only one Successor (the best path)
- **FD is 30720:** Feasible Distance via the Successor
- **via 10.13.0.2 (30720/20480):** Via R3 — metric from R1 is 30720, RD from R3 is 20480
- **via 10.12.0.2 (33280/30720):** Via R2 — metric from R1 is 33280, RD from R2 is 30720

The second path is NOT a Feasible Successor because RD (30720) = FD (30720), not less than FD.

### After Objective 3: Verify Immediate Failover

During the test, observe:
```
R1# show ip eigrp topology 10.0.0.3/32
```

The topology entry should transition to:
- **Active (A)** briefly if there were no Feasible Successors
- **Passive (P)** with a new Successor if a Feasible Successor existed

**With a Feasible Successor:** Failover is sub-millisecond; the route remains in the routing table continuously.
**Without a Feasible Successor:** DUAL reconvergence triggers; you will see "q,u" (query/update) flags and temporary route removal.

### After Objective 4: Unequal-Cost Load Balancing

Run with variance configured:
```
R1# show ip eigrp topology 10.0.0.3/32
```

Expected output with `variance 3`:
```
P 10.0.0.3/32, 2 successors, FD is 30720, serno 7
        via 10.13.0.2 (30720/20480), Serial1
        via 10.12.0.2 (33280/30720), Serial0
```

Now **2 successors** because the second path's metric (33280) ≤ FD × variance (30720 × 3 = 92160).

Verify in the routing table:
```
R1# show ip route eigrp
```

10.0.0.3/32 should have two next-hops listed (via Fa0/0 and Fa1/0).

---

## 7. Verification Cheatsheet

| Command | Purpose |
|---|---|
| `show ip eigrp topology` | Full topology table with FD/RD for all routes |
| `show ip eigrp topology <prefix>` | Inspect one route — Successor, Feasible Successors, RD values |
| `show ip eigrp topology all-links` | All paths including non-feasible ones |
| `show ip route eigrp` | Routing table — active next-hops for each prefix |
| `show ip route <prefix>` | Detailed info for one route — all next-hops shown |
| `show ip eigrp neighbors detail` | K-values and timing per neighbor |
| `show interface <int> stats` | Packet counts — verify traffic across multiple next-hops |

---

## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these steps first!

### Configuration Changes for Variance

<details>
<summary>Click to view R1 Variance Configuration</summary>

```bash
! R1 — Configure variance for unequal-cost load balancing
router eigrp 100
 variance 3
```

No other configuration changes needed. The Feasibility Condition and topology inspection are informational only — they require show commands, not new configs.

</details>

### Verification Commands

<details>
<summary>Click to view Key Verification Commands</summary>

```bash
! Inspect FD/RD for a specific route
show ip eigrp topology 10.0.0.3/32

! Check all paths including non-feasible
show ip eigrp topology all-links

! Verify routing table shows multiple next-hops after variance
show ip route eigrp
show ip route 10.0.0.3

! Verify interface stats show balanced traffic
show interface Fa0/0 | include packets
show interface Fa1/0 | include packets
```

</details>

---

## 9. Troubleshooting Scenarios

Each ticket simulates a real-world fault related to loop-free path selection and load balancing. Inject the fault first, then diagnose using only show commands.

### Workflow

```bash
# 1. Ensure clean state
python3 setup_lab.py
# or
python3 scripts/fault-injection/apply_solution.py

# 2. Inject a fault
python3 scripts/fault-injection/inject_scenario_01.py

# 3. Troubleshoot — diagnose using show commands
# 4. Verify your fix
# 5. Reset between tickets
python3 scripts/fault-injection/apply_solution.py
```

---

### Ticket 1 — No Feasible Successors Available

You receive a report that when the primary link to Branch-B (R3) goes down, traffic to R3 is lost momentarily. You suspect that the Feasibility Condition is not being met, meaning there is no Feasible Successor available for immediate failover.

**Inject:** `python3 scripts/fault-injection/inject_scenario_01.py`

**Symptoms:**
- When R1 Fa1/0 (link to R3) is shut down, R1 loses routes to 10.0.0.3 and 10.23.0.0/30
- The topology table shows only 1 path (via R2), but it is marked as **Active (A)**, not Passive
- DUAL recalculation is in progress; you see "q,u" flags

**Success criteria:**
- A Feasible Successor exists for 10.0.0.3/32
- When the primary link fails, convergence is sub-millisecond
- The route remains in the table continuously during failover

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Inspect the topology before shutdown
R1# show ip eigrp topology 10.0.0.3/32
! Note the FD and both RD values

! The second path (via R2) should have RD < FD to be a Feasible Successor
! If RD from R2 >= FD, the Feasibility Condition is not met
! Check: RD via R2 = _____, FD = _____, is RD < FD?

! If not, examine metrics:
! The problem is likely that R2's path to R3 is too slow (RD too high)
! causing it to exceed the FD of the direct path

! Check bandwidth/delay on R2 Fa0/1 (link to R3)
R2# show interface Fa0/1 | include (BW|Delay)

! Compare to R3 Fa0/1
R3# show interface Fa0/1 | include (BW|Delay)

! If R2 Fa0/1 has incorrect bandwidth or delay, that explains the high RD
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! The typical cause is incorrect bandwidth on R2 Fa0/1
! Default is 100 Mbps, but if it was changed to a lower value, RD increases

! Correct the bandwidth on R2 Fa0/1 to match the link (e.g., 100 Mbps for Fast Ethernet)
R2(config)# interface Fa0/1
R2(config-if)# bandwidth 100
R2(config-if)# no shutdown
R2(config-if)# exit
R2(config)# router eigrp 100
! The metric will recalculate, and now RD via R2 should be < FD

! Verify the topology now shows a Feasible Successor
R1# show ip eigrp topology 10.0.0.3/32
! Should now show: 1 successors (and the secondary path is feasible)

! Test failover by shutting down R1 Fa1/0
R1(config)# interface Fa1/0
R1(config-if)# shutdown
R1# show ip eigrp topology 10.0.0.3/32
! Should remain Passive (P), with the second path now the Successor

! Restore the link
R1(config-if)# no shutdown
```

</details>

---

### Ticket 2 — Variance Not Enabling Unequal-Cost Load Balancing

The network team configured `variance 3` on R1 to enable load balancing to R3, but traffic is still using only one path. When you check the routing table, you still see only a single next-hop for 10.0.0.3/32.

**Inject:** `python3 scripts/fault-injection/inject_scenario_02.py`

**Symptoms:**
- `show ip route eigrp` shows 10.0.0.3/32 with only one next-hop (via R3)
- `show ip eigrp topology 10.0.0.3/32` still shows "1 successors"
- Variance is configured, but it is not taking effect

**Success criteria:**
- 10.0.0.3/32 has 2 next-hops in the routing table
- `show ip eigrp topology` shows "2 successors"
- Unequal-cost load balancing is active

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Check if variance is configured
R1# show run | include variance
! May be empty or incorrectly configured

! Check the metrics to understand why variance should apply
R1# show ip eigrp topology 10.0.0.3/32

! Manually calculate: does the secondary path's metric fit within variance?
! If metric_secondary <= FD * variance, then it should be a Successor

! Example:
! FD = 30720 (via R3)
! Secondary metric via R2 = 33280
! Variance configured = 2
! Does 33280 <= 30720 * 2 = 61440? YES, so it should be a Successor

! If it's not showing as a Successor, either:
! 1. Variance is not configured correctly
! 2. The metric calculation changed and the secondary is no longer feasible
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! Verify or re-configure variance on R1
R1(config)# router eigrp 100
R1(config-router)# variance 3

! Ensure the configuration is saved and applied
R1(config-router)# exit
R1(config)# exit

! Verify the topology now shows 2 successors
R1# show ip eigrp topology 10.0.0.3/32
! Expected: "2 successors, FD is 30720"

! Verify the routing table now shows 2 next-hops
R1# show ip route 10.0.0.3
! Expected: Two lines, one via Fa0/0 (R2) and one via Fa1/0 (R3)
```

</details>

---

### Ticket 3 — FD Not Displayed or Inconsistent Topology Output

When you run `show ip eigrp topology`, some routes display missing FD values or show inconsistent successor/RD information. This suggests a topology database corruption or an adjacency issue.

**Inject:** `python3 scripts/fault-injection/inject_scenario_03.py`

**Symptoms:**
- `show ip eigrp topology` output is sparse or missing FD values
- Some neighbors appear in the adjacency table but not in the topology
- Routing table is incomplete

**Success criteria:**
- All routes show correct FD and RD values
- Topology database is complete and consistent with neighbor count
- Routing table fully populated

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Check neighbor adjacencies first
R1# show ip eigrp neighbors
! Count the neighbors and their state

! Check the topology for the same neighbors
R1# show ip eigrp topology
! Do all neighbors appear as path sources?

! If a neighbor is in the adjacency table but missing from topology,
! it may be a passive interface or network statement issue

! Check the running config for passive interfaces
R1# show run | section eigrp

! Check which interfaces are actively EIGRP-enabled
R1# show ip eigrp interfaces
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! The typical cause is a misconfigured passive-interface or wrong network statement
!
! If a neighbor is missing from EIGRP interfaces:
R1(config)# router eigrp 100
R1(config-router)# no passive-interface FastEthernet0/0
R1(config-router)# no passive-interface FastEthernet1/0

! Ensure network statements are correct
R1(config-router)# network 10.0.0.1 0.0.0.0
R1(config-router)# network 10.12.0.0 0.0.0.3
R1(config-router)# network 10.13.0.0 0.0.0.3
R1(config-router)# exit

! Clear the EIGRP process to force a re-sync of the topology
R1# clear ip eigrp neighbors

! Verify adjacencies and topology restore
R1# show ip eigrp neighbors
R1# show ip eigrp topology
```

</details>

---

### Ticket 4 — Feasibility Condition Misunderstood

A junior engineer reports that they see RD > FD for some paths but believes these should still be Feasible Successors. After investigation, you find the engineer is confusing different routes or misreading the output.

**Inject:** `python3 scripts/fault-injection/inject_scenario_04.py`

**Symptoms:**
- Engineer's confusion: they expect a path to be a Feasible Successor, but it's not listed in the topology
- Manual calculation shows RD > FD, which violates the Feasibility Condition
- The path is marked as simply "via X" but without Successor or Feasible Successor status

**Success criteria:**
- Correctly explain why the path does not qualify as a Feasible Successor
- Document the Feasibility Condition correctly (RD < FD, not RD <= FD)
- Identify the actual Successor and any valid Feasible Successors

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Inspect the route in question
R1# show ip eigrp topology 10.0.0.3/32

! Identify:
! - The Successor and its FD
! - All other paths and their RD values

! Calculate for each path: is RD < FD?
! Example output:
! P 10.0.0.3/32, 1 successors, FD is 30720
!         via 10.13.0.2 (30720/20480) — Successor: RD 20480 < FD 30720? YES
!         via 10.12.0.2 (33280/30720) — Feasible? RD 30720 < FD 30720? NO (equal, not less)

! This path is NOT a Feasible Successor because RD = FD, not < FD
! The condition is strict inequality (less than), not "less than or equal to"
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! No configuration fix needed — this is an educational ticket

! Document the learning:
! Feasibility Condition: RD (from neighbor) < FD (of current Successor)
! Key: strict less-than (<), not less-than-or-equal-to (<=)

! To enable this path as a Feasible Successor, one of:
! 1. Reduce the RD (via metric tuning) so RD < FD
! 2. Increase the FD (by using a worse primary path) — not recommended
! 3. Configure variance to make it a co-Successor (not a Feasible Successor)

! Example variance fix:
R1(config)# router eigrp 100
R1(config-router)# variance 2    ! Allows metric up to FD * 2 = 61440
! Now path with metric 33280 qualifies as a co-Successor
```

</details>

---

### Ticket 5 — Successor Failover is Slow (No Feasible Successor)

A link flaps (up/down/up) and when it goes down, traffic to a destination is lost for several seconds. When the link comes back up, traffic returns immediately. This asymmetry suggests there is no Feasible Successor.

**Inject:** `python3 scripts/fault-injection/inject_scenario_05.py`

**Symptoms:**
- R1 loses reachability to 10.0.0.3 for 3-5 seconds when the primary link fails
- `show ip eigrp topology 10.0.0.3/32` shows "1 successors" (no backup)
- DUAL query/update messages are seen during the outage
- When the link restores, convergence is immediate

**Success criteria:**
- Feasible Successor exists for 10.0.0.3/32
- Link failover is sub-millisecond
- No traffic loss when the primary link fails and a Feasible Successor is available

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Check the current topology with all paths visible
R1# show ip eigrp topology all-links

! Look for 10.0.0.3/32 and identify:
! - The Successor (marked with "Successor")
! - Any other paths and their status (Feasible Successor or plain "via")

! If the secondary path shows RD >= FD, it is not a Feasible Successor
! Example:
! P 10.0.0.3/32, 1 successors, FD is 30720
!         via 10.13.0.2 (30720/20480) — SUCCESSOR
!         via 10.12.0.2 (33280/30720) — NOT FEASIBLE (RD = FD)

! The backup path has RD = 30720, which equals FD (30720)
! The Feasibility Condition requires RD < FD (strict less-than)
! This path cannot be used as a Feasible Successor
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! To create a Feasible Successor, improve the metric of the backup path

! Option 1: Increase bandwidth on the backup path (faster = lower RD)
! R2's path to R3 via Fa0/1 should match R3's interface bandwidth
R2(config)# interface Fa0/1
R2(config-if)# bandwidth 100      ! Match Fa0/0 bandwidth if it's different
R2(config-if)# exit

! Option 2: Enable variance to use the path as a co-Successor
! This makes it a Successor (not a Feasible Successor), but failover is still fast
R1(config)# router eigrp 100
R1(config-router)# variance 3      ! Allows metric <= 30720 * 3 = 92160

! Verify the fix
R1# show ip eigrp topology 10.0.0.3/32
! Expected: Either "2 successors" (with variance) or a Feasible Successor is now listed

! Test failover: shut down the primary link
R1(config-if)# interface Fa1/0
R1(config-if)# shutdown
R1# show ip route 10.0.0.3
! Should still show a route (via the backup path)

R1(config-if)# no shutdown     ! Restore
```

</details>

---

## 10. Lab Completion Checklist

**Core Concepts**
- [ ] Understand the difference between FD (Feasible Distance) and RD (Reported Distance)
- [ ] Explain the Feasibility Condition: RD < FD (strict less-than)
- [ ] Identify Successor (best path) and Feasible Successor (backup meeting FC) for each route
- [ ] Understand variance and how it enables unequal-cost load balancing

**Practical Tasks**
- [ ] Inspect FD/RD values using `show ip eigrp topology <prefix>`
- [ ] Record FD, RD for all routes on R1
- [ ] Verify FC for at least 2 routes (Feasible Successors exist)
- [ ] Simulate a link failure and observe failover behavior (with Feasible Successor)
- [ ] Configure variance on R1: `variance 3`
- [ ] Verify unequal-cost load balancing is active (2 next-hops in routing table)
- [ ] Confirm interface stats show balanced traffic across multiple paths

**Troubleshooting**
- [ ] Ticket 1 diagnosed and resolved (create Feasible Successor via metric tuning)
- [ ] Ticket 2 diagnosed and resolved (variance configuration)
- [ ] Ticket 3 diagnosed and resolved (topology database consistency)
- [ ] Ticket 4 documented (Feasibility Condition clarification)
- [ ] Ticket 5 diagnosed and resolved (add Feasible Successor or variance)

**End-to-End Verification**
- [ ] All neighbors show in `show ip eigrp neighbors`
- [ ] All routes show in `show ip eigrp topology` with complete FD/RD info
- [ ] Routing table reflects configured variance (multiple next-hops where applicable)
- [ ] Pings from R1 to R2, R3, and their loopbacks all succeed
