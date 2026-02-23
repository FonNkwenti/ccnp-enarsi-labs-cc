# EIGRP Lab 03: Metrics — Bandwidth, Delay & K-Values

## 1. Concepts & Skills Covered

**Exam Bullets:**
- 1.9.f Metrics

**What You'll Learn:**
- EIGRP composite metric formula: `Metric = 256 * ((K1*BW + K3*Delay) / (K2*Load+K4)) / (K5/Reliability))`
- Default K-values: K1=1, K3=1, K2=0, K4=0, K5=0 (simplified: `Metric = 256 * (min BW + sum Delay)`
- How bandwidth and delay affect the preferred path
- Using `bandwidth` and `delay` interface commands to manipulate metrics
- Verifying metric changes with `show ip eigrp topology`

---

## 2. Topology & Scenario

Same triangle topology as Lab 01-02. You'll manipulate interface metrics to force a different successor route.

---

## 3. Hardware & Environment Specifications

Same 3 routers (R1, R2, R3), console ports 5001-5003.

---

## 4. Base Configuration

EIGRP Named Mode from Lab 02 (IPv4 + IPv6, dual-stack stable).

---

## 5. Lab Challenge: Core Implementation

### Objective 1: Verify Default Metrics

On R1, run `show ip eigrp topology 10.0.0.2 10.0.0.3` and note the FD and RD values for loopback addresses reached via R2 and R3. Understand which is the preferred path and why.

### Objective 2: Manipulate Bandwidth to Change Successor

On **R2**, reduce the bandwidth on Fa0/0 (toward R1):
```
interface Fa0/0
 bandwidth 100
```

Verify on R1 that R2's loopback is now reached via R3 (path through R3 is now preferred).

### Objective 3: Manipulate Delay on R3

On **R3**, increase the delay on Fa0/0 (toward R1):
```
interface Fa0/0
 delay 10000
```

Verify that R3's loopback metric increases; see if path preference changes.

### Objective 4: Introduce K-Value Mismatch

On **R2**, temporarily set K2=1 (mismatched with R1/R3 default K2=0):
```
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  metric weights 0 1 1 1 0 0
```

Observe the adjacency drop (show ip eigrp neighbors becomes empty). Then restore K-values to default.

---

## 6. Verification & Analysis

```
show ip eigrp topology [prefix] — shows FD, RD, successors, feasible successors
show ip eigrp interfaces detail — shows bandwidth, delay per interface
show ip route eigrp — routing table entries with metrics
```

---

## 7. Verification Cheatsheet

```
show ip eigrp topology
show ip eigrp interfaces detail Fa0/0
show ip route eigrp | include 10.0.0
```

---

## 8. Solutions (Spoiler Alert!)

<details>
<summary>Objective 2 Solution: Reduce Bandwidth on R2 Fa0/0</summary>

```
R2# configure terminal
R2(config)# interface Fa0/0
R2(config-if)# bandwidth 100
R2(config-if)# end
```

Result: Metric to R2 via R1 increases; R1 now prefers R3 as next-hop for reaching R2's loopback.

</details>

<details>
<summary>Objective 3 Solution: Increase Delay on R3 Fa0/0</summary>

```
R3# configure terminal
R3(config)# interface Fa0/0
R3(config-if)# delay 10000
R3(config-if)# end
```

Result: Metric to R3 via R1 increases.

</details>

<details>
<summary>Objective 4 Solution: Restore Default K-Values on R2</summary>

```
R2# configure terminal
R2(config)# router eigrp ENARSI
R2(config-router)# address-family ipv4 unicast autonomous-system 100
R2(config-router-af)# no metric weights 0 1 1 1 0 0
R2(config-router-af)# end
```

Result: Adjacency reforms with R1 and R3; default K-values restored.

</details>

---

## 9. Troubleshooting Scenarios

Each ticket simulates a production fault related to EIGRP metrics and K-values. Inject the fault, diagnose using only `show` commands, then apply a fix.

### Workflow

```bash
# 1. Ensure clean state
python3 scripts/fault-injection/apply_solution.py

# 2. Inject a fault
python3 scripts/fault-injection/inject_scenario_01.py

# 3. Troubleshoot — diagnose using show commands only
# 4. Verify your fix
# 5. Reset between tickets
python3 scripts/fault-injection/apply_solution.py
```

---

### Ticket 1 — Metric to R2 Did Not Change After Bandwidth Configuration

The NOC reports that changing the bandwidth on R2's Fa0/0 interface has had no effect on the EIGRP metric seen from R1.

**Inject:** `python3 scripts/fault-injection/inject_scenario_01.py`

**Symptoms:**
- `show ip eigrp topology 10.0.0.2/32` on R1 shows the same FD as before any bandwidth change
- `show interface Fa0/0 | include BW` on R2 shows the interface default bandwidth
- EIGRP topology is stable — no convergence event occurred

**Success criteria:**
- `show interface Fa0/0 | include BW` on R2 shows `BW 100 Kbit`
- `show ip eigrp topology 10.0.0.2/32` on R1 shows increased FD for the path via R2 Fa0/0
- R1 now prefers R3 as the next-hop for 10.0.0.2/32

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Check bandwidth on R2 Fa0/0
R2# show interface Fa0/0 | include BW
! Default Fast Ethernet BW is 100000 Kbit — if it shows default, bandwidth was removed

! Check R1 topology table for R2's loopback
R1# show ip eigrp topology 10.0.0.2/32
! If the bandwidth command was removed, EIGRP uses default BW and metric is unchanged

! Check running config on R2 for bandwidth command
R2# show running-config interface Fa0/0
! If "bandwidth" line is missing, the fault is confirmed
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! Re-apply the bandwidth manipulation on R2 Fa0/0
R2(config)# interface Fa0/0
R2(config-if)# bandwidth 100
R2(config-if)# end

! Verify metric increased
R1# show ip eigrp topology 10.0.0.2/32
! FD via R2 should now be higher; R1 should prefer R3
```

</details>

---

### Ticket 2 — EIGRP Adjacency to R2 Dropped Immediately

All routes to R2 have disappeared from R1's routing table. The adjacency to R2 was just lost.

**Inject:** `python3 scripts/fault-injection/inject_scenario_02.py`

**Symptoms:**
- `show ip eigrp neighbors` on R1 shows R2 is missing
- `show logging` on R1 shows `%DUAL-5-NBRCHANGE` and K-value mismatch messages
- Routes to 10.0.0.2/32 and 10.12.0.0/30 are gone from `show ip route eigrp`

**Success criteria:**
- R2 reappears in `show ip eigrp neighbors` on R1 and R3
- All routes to R2's networks are restored
- `show ip eigrp neighbors detail` shows matching K-values on all routers

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Check neighbors on R1 — R2 should be missing
R1# show ip eigrp neighbors

! Look for K-value mismatch in the log
R1# show logging | include K-value

! Check K-values on R2
R2# show ip protocols | include K
! R2 will show K1=1, K2=1 (non-default K2) — mismatch with R1/R3 default of K2=0

! Compare K-values with R1
R1# show ip eigrp neighbors detail
! Look for K-values line in detail output
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! Restore default K-values on R2
R2(config)# router eigrp ENARSI
R2(config-router)# address-family ipv4 unicast autonomous-system 100
R2(config-router-af)# no metric weights 0 1 1 1 0 0
R2(config-router-af)# end

! Verify adjacency reforms
R1# show ip eigrp neighbors
! R2 should reappear within the Hello/Hold interval
```

</details>

---

### Ticket 3 — Topology Table Shows Stale Metric for R3

After an interface delay change on R3, R1's topology table shows an outdated metric for R3's loopback. The path is still being used but the metric appears incorrect.

**Inject:** `python3 scripts/fault-injection/inject_scenario_03.py`

**Symptoms:**
- `show ip eigrp interfaces detail Fa0/0` on R3 shows `Delay 50000` (500,000 µs)
- The EIGRP metric for R3's loopback on R1 should reflect this extreme delay
- `show ip eigrp topology 10.0.0.3/32` on R1 may show stale FD until convergence completes

**Success criteria:**
- `show ip eigrp interfaces detail Fa0/0` on R3 shows delay reverted to normal (`Delay 1000`)
- FD for 10.0.0.3/32 on R1 returns to the original pre-fault value
- No convergence events in progress (`P` state in topology table)

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Check current delay on R3 Fa0/0
R3# show interface Fa0/0 | include DLY
! Expected: DLY 500000 usec (extreme value from fault injection)

! Check EIGRP interfaces on R3
R3# show ip eigrp interfaces detail Fa0/0
! Look for "Delay 50000" — in tens of microseconds, equals 500ms

! Check topology table on R1 for R3's loopback
R1# show ip eigrp topology 10.0.0.3/32
! FD should have increased significantly due to extreme delay

! Force re-convergence if still showing stale value
R1# clear ip eigrp neighbors 10.13.0.2
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! Restore the lab-configured delay on R3 Fa0/0
R3(config)# interface Fa0/0
R3(config-if)# delay 10000
R3(config-if)# end

! Verify topology table updated
R1# show ip eigrp topology 10.0.0.3/32
! FD should return to expected value reflecting delay 10000
```

</details>

---

### Ticket 4 — Bandwidth Change Has No Effect on EIGRP Metric

An engineer attempted to lower R2's metric by setting a lower bandwidth on Fa0/0. However, the EIGRP metric is unchanged after the bandwidth command was applied.

**Inject:** `python3 scripts/fault-injection/inject_scenario_04.py`

**Symptoms:**
- `show running-config interface Fa0/0` on R2 shows the `bandwidth` command is present
- `show ip eigrp topology 10.0.0.2/32` on R1 shows the same FD — bandwidth did not affect the metric
- Adjacency to R2 may have dropped and reformed due to K-value mismatch side effect

**Success criteria:**
- K-values on R2 match R1/R3 (default: K1=1, K2=0, K3=1, K4=0, K5=0)
- Changing bandwidth on R2 Fa0/0 now produces a measurable metric change on R1
- `show ip eigrp neighbors detail` shows all routers have matching K-values

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Check K-values on R2 — K2=1 makes bandwidth irrelevant to the simplified metric formula
R2# show ip protocols | include K
! If K2=1, the metric formula changes and bandwidth alone does not drive the metric

! Verify adjacency is up
R1# show ip eigrp neighbors
! If R2 is missing, K-value mismatch caused adjacency to drop

! Compare K-values with R1
R1# show ip eigrp neighbors detail
! K-values line should show K1=1, K2=0, K3=1, K4=0, K5=0 on R1
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! Remove non-default K-values from R2
R2(config)# router eigrp ENARSI
R2(config-router)# address-family ipv4 unicast autonomous-system 100
R2(config-router-af)# no metric weights 0 1 1 1 0 0
R2(config-router-af)# end

! Verify K-values restored to default
R2# show ip protocols | include K
! Should show K1=1, K2=0, K3=1, K4=0, K5=0

! Now verify bandwidth change takes effect
R1# show ip eigrp topology 10.0.0.2/32
! FD should now reflect the configured bandwidth on R2 Fa0/0
```

</details>

---

### Ticket 5 — Successor Path Unchanged After Delay Modification

An engineer changed the delay on R3's Fa0/0 to influence path selection from R1. Despite the change, R1's routing table still shows R3 as the Successor with the same metric.

**Inject:** `python3 scripts/fault-injection/inject_scenario_05.py`

**Symptoms:**
- `show ip eigrp topology` on R1 shows no change in FD for routes via R3
- `show ip eigrp interfaces` on R3 does not list Fa0/0 as an EIGRP interface
- Delay change on R3 Fa0/0 is visible with `show interface Fa0/0 | include DLY` but has no EIGRP effect

**Success criteria:**
- R3's Fa0/0 appears in `show ip eigrp interfaces` on R3
- Delay change on R3 Fa0/0 produces a corresponding metric change seen from R1
- EIGRP hellos are being sent/received on R3 Fa0/0

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Check EIGRP interfaces on R3 — Fa0/0 should appear
R3# show ip eigrp interfaces
! If Fa0/0 is missing, it is either passive or not matched by a network statement

! Check for passive-interface
R3# show ip protocols | include Passive
! If "FastEthernet0/0" appears here, passive-interface is the fault

! Verify EIGRP adjacency with R1
R3# show ip eigrp neighbors
! R1 (10.13.0.1) should be a neighbor — if missing, Fa0/0 is not participating in EIGRP
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! Remove passive-interface from R3 Fa0/0
R3(config)# router eigrp ENARSI
R3(config-router)# address-family ipv4 unicast autonomous-system 100
R3(config-router-af)# no passive-interface Fa0/0
R3(config-router-af)# end

! Verify Fa0/0 is now active in EIGRP
R3# show ip eigrp interfaces
! Fa0/0 should now appear in the interface list

! Verify adjacency with R1 is established
R3# show ip eigrp neighbors
! 10.13.0.1 (R1) should reappear
```

</details>

---

## 10. Lab Completion Checklist

- [ ] Default metrics verified on all loopbacks
- [ ] Bandwidth manipulation tested; path preference changed
- [ ] Delay manipulation tested; metric increased
- [ ] K-value mismatch introduced and adjacency dropped
- [ ] K-values restored and adjacency reformed
- [ ] 5 troubleshooting tickets completed
