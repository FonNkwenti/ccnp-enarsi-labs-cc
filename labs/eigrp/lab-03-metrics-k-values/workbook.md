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

### Ticket 1 — Metrics Not Reflecting Bandwidth Change

<details>
<summary>Diagnosis: Check interface bandwidth setting</summary>

```
show interface Fa0/0 | include BW
show ip eigrp interfaces detail Fa0/0 | include "Bandwidth"
```

</details>

<details>
<summary>Fix: Verify bandwidth command applied</summary>

```
interface Fa0/0
 bandwidth 100
```

</details>

---

### Ticket 2 — K-Value Mismatch Not Detected

Check K-values on all routers; ensure they match.

---

### Ticket 3 — Topology Not Updating After Metric Change

Use `clear ip eigrp neighbors` to force re-convergence.

---

### Ticket 4 — Bandwidth Command Applied but No Effect

Ensure EIGRP is using default K-values (K2=0). If K2!=0, bandwidth changes won't affect metric.

---

### Ticket 5 — Successor Still Unchanged After Delay Increase

Verify the interface is part of EIGRP. Use `show ip eigrp interfaces` to confirm.

---

## 10. Lab Completion Checklist

- [ ] Default metrics verified on all loopbacks
- [ ] Bandwidth manipulation tested; path preference changed
- [ ] Delay manipulation tested; metric increased
- [ ] K-value mismatch introduced and adjacency dropped
- [ ] K-values restored and adjacency reformed
- [ ] 5 troubleshooting tickets completed
