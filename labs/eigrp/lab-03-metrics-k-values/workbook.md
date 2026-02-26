# Lab 03: EIGRP Metrics — Bandwidth, Delay & K-Values

**Chapter:** EIGRP | **Difficulty:** Intermediate | **Time:** 90 min
**Blueprint:** 1.9.f — Troubleshoot EIGRP Metrics

---

## Section 1 — Concepts & Skills Covered

**Exam Objective:** CCNP ENARSI 1.9.f — EIGRP Metrics

This lab explores how EIGRP builds its composite metric and how interface
parameters control path selection. You will read the topology table to understand
the default metric, tune bandwidth and delay to redirect traffic, and deliberately
introduce a K-value mismatch to observe and resolve adjacency failure.

### EIGRP Composite Metric

EIGRP selects paths using a composite metric computed from up to five K-value-weighted interface parameters. With the default K-values (K1=1, K3=1, all others 0), the formula reduces to:

```
M = 256 × (10^7 / BW_min + delay_total / 10)
```

Where `BW_min` is the lowest interface bandwidth (in kbps) along the path, and `delay_total` is the cumulative interface delay (in tens of microseconds). Default interface values:

| Interface Type | Default Bandwidth | Default Delay | Delay (tens-of-µs) |
|----------------|-------------------|---------------|--------------------|
| FastEthernet | 100,000 kbps | 1,000 µs | 100 |
| Loopback | 8,000,000 kbps | 5,000 µs | 500 |
| Serial | 1,544 kbps | 20,000 µs | 2,000 |

### K-Values

K-values (K1–K5) are multipliers that control which interface parameters contribute to the metric. Only K1 and K3 are active by default:

| K-Value | Controls | Default | Notes |
|---------|----------|---------|-------|
| K1 | Bandwidth | 1 | Inverse of minimum bandwidth along path |
| K2 | Load | 0 | Interface utilization (0–255); disabled by default |
| K3 | Delay | 1 | Cumulative path delay |
| K4 | Reliability | 0 | Interface reliability (0–255); disabled by default |
| K5 | MTU | 0 | Maximum Transmission Unit; disabled by default |

Because K2, K4, and K5 default to 0, load, reliability, and MTU do not contribute to path selection unless explicitly enabled with `metric weights`.

### Interface Metric Commands

Two interface commands directly influence the EIGRP metric without changing actual traffic behavior:

```
interface FastEthernet0/0
 bandwidth 10000          ! Override logical BW (kbps) — affects metric only
 delay 1000               ! Override delay (tens-of-µs) — affects metric only
```

> **Important:** The `bandwidth` command does **not** throttle or shape traffic. It only overrides the value EIGRP (and OSPF cost) uses in its metric calculation. Actual link throughput is unchanged.

### K-Value Mismatch

K-values are advertised in EIGRP HELLO packets. When two neighbors have different K-value configurations, the adjacency fails immediately — no HELLO exchange will succeed. The router logs a characteristic diagnostic message:

```
%DUAL-5-NBRCHANGE: EIGRP-IPv4 100: Neighbor 10.12.0.2 (FastEthernet0/0) is down: K-value mismatch
```

This is one of the most common ENARSI exam troubleshooting scenarios. Always check `show ip protocols` on both sides to compare K-values when an adjacency refuses to form.

**Skills this lab develops:**

| Skill | Description |
|-------|-------------|
| Composite metric formula | M = 256 × (10^7 / BW_min + delay_total / 10) |
| Active K-values | K1 (bandwidth) and K3 (delay) are 1 by default; K2/K4/K5 = 0 |
| Bandwidth tuning | `bandwidth` overrides the value EIGRP uses — does not throttle traffic |
| Delay tuning | `delay` (in tens-of-microseconds) accumulates at every hop |
| K-value mismatch | Mismatched K-values in HELLO packets silently drop adjacency |
| Topology table reading | Successor, Feasible Distance, Reported Distance per prefix |

---

## 2. Topology & Scenario

**Enterprise Scenario:** As a lead network engineer at Acme Corp, you manage
a three-router EIGRP domain connecting the corporate hub (R1) to Branch-A (R2)
and Branch-B (R3). The direct WAN link between the hub and Branch-A
(R1 Fa0/0 ↔ R2 Fa0/0) is over-subscribed at peak hours. The network team
needs to redirect R2-destined traffic from R1 through Branch-B as a transit,
using EIGRP metric tuning rather than a static override. You must also be able
to recognize and resolve K-value mismatches — a subtle but total adjacency
killer that the ENARSI exam tests explicitly.

**ASCII Topology:**

```
              ┌─────────────────────────┐
              │           R1            │
              │      (Hub / Core)       │
              │   Lo0: 10.0.0.1/32      │
              └──────┬───────────┬──────┘
           Fa0/0     │           │     Fa1/0
     10.12.0.1/30    │           │   10.13.0.1/30
                     │           │
     10.12.0.2/30    │           │   10.13.0.2/30
           Fa0/0     │           │     Fa0/0
     ┌───────────────┘           └───────────────┐
     │                                           │
┌────┴──────────────┐           ┌────────────────┴────┐
│       R2          │           │        R3           │
│   (Branch A)      │           │    (Branch B)       │
│ Lo0: 10.0.0.2/32  │           │  Lo0: 10.0.0.3/32   │
└─────────┬─────────┘           └──────────┬──────────┘
      Fa0/1│                               │Fa0/1
10.23.0.1/30│                             │10.23.0.2/30
            └─────────────────────────────┘
                       10.23.0.0/30
```

**Active Links:**

| Link | Source | Interface | Destination | Interface | Subnet |
|------|--------|-----------|-------------|-----------|--------|
| L1 | R1 | Fa0/0 | R2 | Fa0/0 | 10.12.0.0/30 |
| L2 | R1 | Fa1/0 | R3 | Fa0/0 | 10.13.0.0/30 |
| L3 | R2 | Fa0/1 | R3 | Fa0/1 | 10.23.0.0/30 |

---

## 3. Hardware & Environment Specifications

**Platform:** GNS3 — Dynamips c7200, IOS 15.3(3)XB12

**Device Inventory:**

| Device | Role | Platform | IOS Image |
|--------|------|----------|-----------|
| R1 | Hub / Core | c7200 | c7200-adventerprisek9-mz.153-3.XB12.image |
| R2 | Branch A | c7200 | c7200-adventerprisek9-mz.153-3.XB12.image |
| R3 | Branch B | c7200 | c7200-adventerprisek9-mz.153-3.XB12.image |

**Adapter Cards:**

| Device | Slot | Card | Interfaces |
|--------|------|------|------------|
| R1 | Slot 0 | C7200-IO-FE | Fa0/0 |
| R1 | Slot 1 | PA-2FE-TX | Fa1/0, Fa1/1 |
| R2 | Slot 0 | C7200-IO-2FE | Fa0/0, Fa0/1 |
| R3 | Slot 0 | C7200-IO-2FE | Fa0/0, Fa0/1 |

**Cabling Table:**

| Link | Device A | Interface | Device B | Interface | Subnet IPv4 | Subnet IPv6 |
|------|----------|-----------|----------|-----------|-------------|-------------|
| L1 | R1 | Fa0/0 | R2 | Fa0/0 | 10.12.0.0/30 | 2001:DB8:12::/64 |
| L2 | R1 | Fa1/0 | R3 | Fa0/0 | 10.13.0.0/30 | 2001:DB8:13::/64 |
| L3 | R2 | Fa0/1 | R3 | Fa0/1 | 10.23.0.0/30 | 2001:DB8:23::/64 |

**Console Access Table:**

| Device | Console Port | Connection Command |
|--------|-------------|-------------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |

---

## 4. Base Configuration

The `initial-configs/` directory contains everything from Lab 02 solutions.
The following is already configured on all routers:

**Pre-configured:**

- Hostname and `no ip domain-lookup`
- `ipv6 unicast-routing` on all routers
- All FastEthernet and Loopback0 interfaces with IPv4 (/30, /32) and IPv6 addressing
- EIGRP Named Mode process `ENARSI`
  - `address-family ipv4 unicast autonomous-system 100` — correct network statements per router
  - `address-family ipv6 unicast autonomous-system 100`
  - `eigrp router-id` in both address families
  - `no auto-summary` in IPv4 AF
  - `eigrp log-neighbor-changes` in both AFs

**NOT pre-configured (your tasks):**

- Interface bandwidth customization
- Interface delay customization
- EIGRP metric weights (K-values)

---

## 5. Lab Challenge: Core Implementation

### Task 1: Verify the Default EIGRP Composite Metric

- On all three routers, confirm the active K-values match the EIGRP default
  (K1=1, K2=0, K3=1, K4=0, K5=0, TOS=0)
- On R1, examine the EIGRP topology table for R2's loopback (10.0.0.2/32)
  - Record the Feasible Distance (FD) and the Reported Distance (RD)
  - Record the successor interface and next-hop address
  - Note the minimum bandwidth and total delay shown in the vector metric block
- Using the EIGRP composite metric formula below, manually verify that the
  displayed FD is consistent with the reported bandwidth and delay values:
  - **Formula:** M = 256 × (10^7 / BW_min + delay_total / 10)
  - Where `BW_min` is in kbps and `delay_total` is in microseconds

**Verification:** `show ip eigrp topology 10.0.0.2/32` on R1 must show the
successor via Fa0/0 (direct link to R2) and display the vector metric breakdown.

---

### Task 2: Manipulate Interface Bandwidth and Delay to Change the Preferred Path

- On R1's interface toward R2 (Fa0/0), set the bandwidth to 512 kbps
- On the same interface, set the delay to 2000 (in tens-of-microseconds)
- Allow EIGRP to reconverge — watch for `%DUAL-5-NBRCHANGE` and
  `%EIGRP-5-NBRCHANGE` log messages indicating topology recalculation
- Confirm that R1's EIGRP topology table now shows the path via R3 (Fa1/0)
  as the new successor for R2's loopback (10.0.0.2/32)

**Verification:** `show ip eigrp topology 10.0.0.2/32` on R1 must show
successor via Fa1/0 with a lower FD than the now-degraded direct path via Fa0/0.

---

### Task 3: Verify Metric Changes in the Routing Table

- Confirm R1's IPv4 routing table shows 10.0.0.2/32 reachable via next-hop
  10.13.0.2 on interface Fa1/0 (the R3 transit path)
- Use `show ip eigrp topology all-links 10.0.0.2/32` to view both paths —
  confirm the degraded direct path via Fa0/0 shows a dramatically larger FD
- On R2 and R3, verify their routing tables are unaffected (they still use
  their own direct connections)

**Verification:** `show ip route 10.0.0.2` on R1 must show the route learned
via 10.13.0.2 (R3), not 10.12.0.2 (R2 direct). The metric should reflect the
via-R3 three-interface cumulative delay at default FastEthernet values.

---

### Task 4: Introduce a K-Value Mismatch and Restore

- On R1, under the Named Mode EIGRP process IPv4 address-family, configure
  metric weights with TOS=0, K1=1, K2=1, K3=1, K4=0, K5=0 (a non-default K2=1)
- Observe the console log — both R2 and R3 should report K-value mismatch
  and drop their EIGRP adjacency with R1
- Verify that `show ip eigrp neighbors` on R2 and R3 shows no active neighbors
- On R1, restore the default K-values: TOS=0, K1=1, K2=0, K3=1, K4=0, K5=0
- Verify adjacencies re-establish with both R2 and R3 within one dead interval

**Verification:** `show ip eigrp neighbors` on R1 must show two active
neighbors (R2 and R3) after restoration. `show ip eigrp topology` must
repopulate with all routes.

---

## 6. Verification & Analysis

### 6.1 Default Metric Baseline (Before Any Tuning)

```
R1# show ip eigrp topology 10.0.0.2/32
EIGRP-IPv4 VR(ENARSI) Topology Entry for AS(100)/ID(10.0.0.1) for 10.0.0.2/32
  State is Passive, Query origin flag is 1, 1 Successor(s), FD is 130816
  Descriptor Blocks:
  10.12.0.2 (FastEthernet0/0), from 10.12.0.2, Send flag is 0x0
      Composite metric is (130816/128256), route is Internal
      Vector metric:
        Minimum bandwidth is 100000 Kbit    ! ← default FastEthernet BW
        Total delay is 5200 microseconds    ! ← Lo0(5000) + Fa0/0(100) + Fa0/0(100)
        Reliability is 255/255
        Load is 1/255
        Minimum MTU is 1500
        Hop count is 1
```

> Note: The loopback0 interface default delay is 5000 usec. EIGRP accumulates
> delay across all interfaces along the path — Loopback0 (5000) + R2 Fa0/0 (100)
> + R1 Fa0/0 (100) = 5200 usec total for the direct one-hop path.

### 6.2 After Bandwidth and Delay Manipulation (Task 2)

```
R1# show ip eigrp topology 10.0.0.2/32
EIGRP-IPv4 VR(ENARSI) Topology Entry for AS(100)/ID(10.0.0.1) for 10.0.0.2/32
  State is Passive, Query origin flag is 1, 1 Successor(s), FD is 133376
  Descriptor Blocks:
  10.13.0.2 (FastEthernet1/0), from 10.13.0.2, Send flag is 0x0    ! ← NEW successor via R3
      Composite metric is (133376/130816), route is Internal
      Vector metric:
        Minimum bandwidth is 100000 Kbit                            ! ← via-R3 path at full FA BW
        Total delay is 5400 microseconds                            ! ← one extra FA hop via R3
        ...
  10.12.0.2 (FastEthernet0/0), from 10.12.0.2, Send flag is 0x0
      Composite metric is (5242880/128256), route is Internal       ! ← massive metric — degraded link
      Vector metric:
        Minimum bandwidth is 512 Kbit                               ! ← bandwidth 512 configured
        Total delay is 20200 microseconds                           ! ← delay 2000 (×10 usec) + normal hops
```

### 6.3 Routing Table Confirms New Preferred Path

```
R1# show ip route 10.0.0.2
Routing entry for 10.0.0.2/32
  Known via "eigrp 100", distance 90, metric 133376
  Redistributing via eigrp 100
  Last update from 10.13.0.2 on FastEthernet1/0, ...
  Routing Descriptor Blocks:
  * 10.13.0.2, from 10.13.0.2, via FastEthernet1/0   ! ← via R3 transit, NOT direct
```

### 6.4 K-Value Mismatch — Adjacency Loss

```
R1# show ip eigrp neighbors
EIGRP-IPv4 Neighbors for AS(100)
H   Address         Interface       Hold  Uptime   SRTT   RTO  Q  Seq
                                   (sec)           (ms)       Cnt Num
! ← empty — both R2 and R3 have dropped adjacency due to K-value mismatch

! Syslog on R2:
%DUAL-5-NBRCHANGE: EIGRP-IPv4 100: Neighbor 10.12.0.1 (FastEthernet0/0)
  is down: K-value mismatch                                          ! ← exact symptom to look for
```

### 6.5 Adjacency Re-establishment After Restore

```
R1# show ip eigrp neighbors
EIGRP-IPv4 Neighbors for AS(100)
H   Address         Interface       Hold  Uptime   SRTT   RTO  Q  Seq
                                   (sec)           (ms)       Cnt Num
0   10.12.0.2       Fa0/0             12  00:00:18   14   200  0  8   ! ← R2 restored
1   10.13.0.2       Fa1/0             11  00:00:16   12   200  0  7   ! ← R3 restored
```

---

## 7. Verification Cheatsheet

### EIGRP Composite Metric Formula

```
M = 256 × (10^7 / BW_min  +  delay_total / 10)

  BW_min      = minimum bandwidth along the entire path (kbps)
  delay_total = sum of all interface delays along the path (microseconds)
```

| Default Interface Values | Bandwidth | Delay |
|--------------------------|-----------|-------|
| FastEthernet | 100,000 kbps | 100 usec |
| Loopback0 | 8,000,000 kbps | 5,000 usec |
| Serial (T1) | 1,544 kbps | 20,000 usec |

> **Exam tip:** `bandwidth` does NOT throttle actual traffic — it only changes the
> value EIGRP uses in its metric calculation. Mixing it up with traffic shaping
> is a common ENARSI exam trap.

### Interface Metric Tuning

```
interface FastEthernet0/0
 bandwidth 512       ! kbps — minimum BW EIGRP reports for this interface
 delay 2000          ! tens-of-microseconds (2000 × 10 = 20,000 usec)
```

| Command | Purpose |
|---------|---------|
| `bandwidth <kbps>` | Override BW used by EIGRP metric (and other protocols) |
| `delay <tens-of-usec>` | Override delay added to path delay accumulation |
| `no bandwidth` | Restore interface default bandwidth |
| `no delay` | Restore interface default delay |

> **Exam tip:** The `delay` command value is in tens of microseconds.
> `delay 10` = 100 usec (FastEthernet default). `delay 2000` = 20,000 usec.
> `show interfaces` always reports delay in microseconds, not tens-of-microseconds.

### K-Value Configuration

```
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  metric weights 0 1 0 1 0 0    ! TOS K1 K2 K3 K4 K5 — this is the default
```

| Command | Purpose |
|---------|---------|
| `metric weights 0 K1 K2 K3 K4 K5` | Set K-values (TOS field is always 0) |
| `no metric weights` | Reset all K-values to default (K1=1, K3=1, others=0) |

> **Exam tip:** K-values must be **identical** on both ends of every EIGRP
> adjacency. A mismatch causes immediate adjacency loss. The log message
> `K-value mismatch` is the diagnostic indicator. K4 and K5 interact only when
> K5 > 0 — enabling reliability-based metrics rarely used in production.

### Verification Commands

| Command | What to Look For |
|---------|-----------------|
| `show ip eigrp topology` | All active routes — FD, RD, successor, interface |
| `show ip eigrp topology all-links` | All paths including non-successors |
| `show ip eigrp topology <prefix>` | Full vector metric breakdown for one prefix |
| `show ip eigrp neighbors` | Active adjacencies — empty = mismatch or link down |
| `show interfaces <int>` | Live BW and Delay values (delay shown in usec) |
| `show ip route eigrp` | Final IPv4 routing table for EIGRP-learned routes |
| `show ip protocols` | K-values, AS number, network statements, router-id |

### Wildcard Mask Quick Reference

| Subnet Mask | Wildcard | Common Use |
|-------------|----------|------------|
| 255.255.255.252 | 0.0.0.3 | /30 point-to-point link |
| 255.255.255.0 | 0.0.0.255 | /24 LAN segment |
| 255.255.255.255 | 0.0.0.0 | /32 host route (loopback) |

### Common EIGRP Metric Failure Causes

| Symptom | Likely Cause |
|---------|-------------|
| All neighbors drop simultaneously | K-value mismatch (`metric weights` misconfigured) |
| Suboptimal path despite link being up | Low `bandwidth` or high `delay` on preferred interface |
| Route flapping after metric change | `delay` applied to only one side of the link |
| Metric in topology table doesn't match formula | Loopback delay (5000 usec default) not accounted for |
| Adjacency lost after `metric weights` change | K2, K4, or K5 set to non-zero — check all neighbors |

---

## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these steps first!

### Task 1: Verify Default Metric

<details>
<summary>Click to view Verification Commands</summary>

```bash
! On R1 — confirm default K-values
show ip protocols
! Look for: K1=1, K2=0, K3=1, K4=0, K5=0 under the ENARSI process

! On R1 — examine full metric breakdown for R2's loopback
show ip eigrp topology 10.0.0.2/32
! Note the FD, RD, minimum bandwidth, and total delay in the vector metric block

! On R1 — confirm interface defaults
show interfaces Fa0/0 | include BW|DLY
! Expected: BW 100000 Kbit, DLY 100 usec
```

</details>

---

### Task 2: Manipulate Bandwidth and Delay

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1
interface FastEthernet0/0
 bandwidth 512
 delay 2000
```

</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
! On R1 — wait for convergence then verify new successor
show ip eigrp topology 10.0.0.2/32
! Successor must now be 10.13.0.2 via FastEthernet1/0 (via R3)
! The via-Fa0/0 entry should show a dramatically larger FD
```

</details>

---

### Task 3: Verify Metric in Routing Table

<details>
<summary>Click to view Verification Commands</summary>

```bash
! On R1
show ip route 10.0.0.2
! Must show: D 10.0.0.2/32 [90/...] via 10.13.0.2, FastEthernet1/0
! NOT via 10.12.0.2 (the degraded direct link)

show ip eigrp topology all-links 10.0.0.2/32
! Both paths visible:
!   via 10.13.0.2 Fa1/0 — smaller FD (successor)
!   via 10.12.0.2 Fa0/0 — large FD (degraded by bandwidth 512 + delay 2000)
```

</details>

---

### Task 4: K-Value Mismatch and Restore

<details>
<summary>Click to view R1 — Fault Introduction and Fix</summary>

```bash
! STEP 1 — Introduce mismatch on R1 (observe adjacency loss)
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  metric weights 0 1 1 1 0 0
! Watch syslog: %DUAL-5-NBRCHANGE ... is down: K-value mismatch

! Verify impact
show ip eigrp neighbors
! Expected: empty — both R2 and R3 dropped

! STEP 2 — Restore default K-values on R1
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  metric weights 0 1 0 1 0 0

! Verify restoration (allow up to 15 seconds for hold timer)
show ip eigrp neighbors
! R2 and R3 must reappear

show ip eigrp topology
! Topology table must repopulate with all prefixes
```

</details>

---

## 9. Troubleshooting Scenarios

Each ticket simulates a real-world fault. Inject the fault first, then
diagnose and fix using only `show` commands and the topology table.

### Workflow

```bash
python3 setup_lab.py                                   # reset to known-good state
python3 scripts/fault-injection/inject_scenario_01.py  # Ticket 1
python3 scripts/fault-injection/apply_solution.py      # restore after each ticket
```

---

### Ticket 1 — R2 and R3 Simultaneously Report No Active EIGRP Neighbors Toward the Hub

The NOC reports that both branch routers lost their EIGRP adjacency with R1
at the same time. No interface has gone down and all links show physical up/up.
The outage occurred minutes after a configuration push to R1.

**Inject:** `python3 scripts/fault-injection/inject_scenario_01.py`

**Success criteria:** `show ip eigrp neighbors` on R2 and R3 each show R1 as
an active neighbor with a non-zero uptime.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R2: `show ip eigrp neighbors` — confirm R1 (10.12.0.1) is absent
2. Check R1's console log for `%DUAL-5-NBRCHANGE ... K-value mismatch`
3. On R1: `show ip protocols` — inspect K-values under the ENARSI process
4. On R2: `show ip protocols` — compare K-values to R1
5. A non-zero K2, K4, or K5 on one side while the other side has 0 confirms mismatch

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R1 — restore default K-values
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  metric weights 0 1 0 1 0 0
```

Verify: `show ip eigrp neighbors` on R2 and R3 — R1 must reappear within one
dead interval (typically 15 seconds for FastEthernet).

</details>

---

### Ticket 2 — Traffic from R1 to R3's Loopback Is Routing via an Unexpected Transit Path

A flow monitor shows that packets from R1 destined for R3's loopback (10.0.0.3/32)
are taking a two-hop path through R2 instead of the direct R1–R3 Fa1/0 link.
Both links appear up and all EIGRP adjacencies are healthy.

**Inject:** `python3 scripts/fault-injection/inject_scenario_02.py`

**Success criteria:** `show ip route 10.0.0.3` on R1 shows the route via
next-hop 10.13.0.2 on Fa1/0 (direct), not through R2.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R1: `show ip eigrp topology 10.0.0.3/32` — identify the current successor
   and its interface; confirm it is NOT via Fa1/0
2. On R1: compare the FD for both paths using `show ip eigrp topology all-links 10.0.0.3/32`
3. On R1: `show interfaces Fa1/0 | include BW|DLY` — check for abnormally high delay
4. Abnormal delay value on Fa1/0 identified as the root cause — elevating the
   metric for the direct R1–R3 path above the via-R2 metric

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R1
interface FastEthernet1/0
 no delay
```

Verify: `show ip eigrp topology 10.0.0.3/32` — the successor must revert to
Fa1/0 (10.13.0.2 direct) after EIGRP reconverges.

</details>

---

### Ticket 3 — R2's Route to R1's Loopback Is Present but Metrics Appear Inconsistent

R2 reports that it can reach R1's loopback (10.0.0.1/32) but the metric
displayed in `show ip route` is unexpectedly large. A colleague recently
adjusted EIGRP metric weights on R2 for a lab exercise and reports they
restored them, but the restoration may have been incomplete.

**Inject:** `python3 scripts/fault-injection/inject_scenario_03.py`

**Success criteria:** `show ip eigrp neighbors` on R2 shows R1 as an active
neighbor; R2's route to 10.0.0.1/32 shows normal EIGRP metrics.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. On R2: `show ip eigrp neighbors` — if R1 is absent, K-value mismatch is confirmed
2. On R2: `show ip protocols` — examine K-values under the ENARSI process
3. On R1: `show ip protocols` — compare K-values to R2
4. If K4 or K5 is non-zero on R2 and zero on R1, the restoration was incomplete —
   `no metric weights` restores all K-values to factory default simultaneously

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R2
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  no metric weights
```

Verify: `show ip eigrp neighbors` on R2 shows R1 active; `show ip route 10.0.0.1`
on R2 shows normal metric with next-hop 10.12.0.1 via Fa0/0.

</details>

---

## 10. Lab Completion Checklist

### Core Implementation

- [ ] Default K-values verified on all three routers (K1=1, K2=0, K3=1, K4=0, K5=0)
- [ ] EIGRP topology table entry for 10.0.0.2/32 read from R1 — FD, RD, and
      vector metric breakdown recorded before any changes
- [ ] `bandwidth 512` configured on R1 Fa0/0
- [ ] `delay 2000` configured on R1 Fa0/0
- [ ] EIGRP reconvergence observed; R1 topology table shows via-R3 as new successor
- [ ] `show ip route 10.0.0.2` on R1 confirms next-hop is 10.13.0.2 (via R3)
- [ ] K-value mismatch introduced on R1 — both R2 and R3 drop adjacency confirmed
- [ ] K-values restored to default on R1 — R2 and R3 adjacencies re-established

### Troubleshooting

- [ ] Ticket 1 resolved: K-value mismatch on R1 identified via `show ip protocols`
      and `%DUAL-5-NBRCHANGE` log; both branch adjacencies restored
- [ ] Ticket 2 resolved: Abnormal delay on R1 Fa1/0 identified and removed;
      R3's loopback now routes via direct Fa1/0
- [ ] Ticket 3 resolved: Incomplete K-value restoration on R2 identified;
      `no metric weights` applied; R1 loopback reachable with normal metric
