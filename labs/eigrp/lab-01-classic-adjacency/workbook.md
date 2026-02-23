# EIGRP Lab 01 — Classic Mode: Neighbor Adjacency & Basic IPv4

**Exam:** CCNP ENARSI 300-410
**Difficulty:** Foundation
**Estimated Time:** 60 minutes

---

## 1. Concepts & Skills Covered

### Blueprint Coverage

| Blueprint ID | Topic |
|---|---|
| 1.9.b | Troubleshoot EIGRP neighbor adjacency |

### Key Concepts

**EIGRP Neighbor Formation Process**
EIGRP forms neighbor adjacencies by exchanging **Hello** packets on each interface. Two routers become neighbors only when their Hello packets match on:
- **Autonomous System (AS) number** — must be identical
- **K-values** — the metric weighting factors (default: K1=1, K2=0, K3=1, K4=0, K5=0)
- **Subnet** — neighbors must share the same subnet on the connecting interface
- **Authentication** — if configured, must match (not applicable in this lab)

**The EIGRP Neighbor Table Sequence**
1. Router sends **Hello** out an EIGRP-enabled interface
2. Receiving router replies with a **Hello** (peer verification)
3. Routers exchange **Full Update** packets — all topology information
4. Neighbor relationship enters **UP** state: `(Up)` in `show ip eigrp neighbors`

**EIGRP network Command and Wildcard Masks**
The `network` command inside `router eigrp <AS>` enables EIGRP on interfaces whose IP addresses match the specified range. Using exact-host wildcard masks (`0.0.0.0`) is best practice for precision:
```
network 10.12.0.0 0.0.0.3   ! Enables EIGRP on any interface in 10.12.0.0–10.12.0.3
network 10.0.0.1 0.0.0.0    ! Enables EIGRP on exactly the 10.0.0.1 interface (Loopback0)
```

**Passive Interface**
A passive interface receives Hellos but does not send them. The result: no adjacency can form. Used to suppress EIGRP on interfaces that connect to end hosts or untrusted networks — **never** on router-to-router links.

**no auto-summary**
In classic EIGRP, auto-summary is **enabled by default** and summarizes routes to classful boundaries at major network boundaries. This causes routing black holes with discontiguous networks. Best practice: always disable it with `no auto-summary`.

**EIGRP Timers**
- **Hello interval**: 5 seconds (broadcast/point-to-point), 60 seconds (NBMA)
- **Hold time**: 15 seconds (3× hello). If no Hello received within hold time, neighbor is declared down.

---

## 2. Topology & Scenario

### Enterprise Scenario

Acme Corp is deploying EIGRP across its enterprise WAN. R1 is the hub router at the corporate headquarters. R2 serves Branch Office A and R3 serves Branch Office B. Each branch connects directly to the hub and to each other for redundancy.

Your task is to configure EIGRP classic mode (AS 100) across all three routers, ensuring full IP reachability between all sites including loopback interfaces used for network management.

### Topology Diagram

> Open `topology.drawio` in Draw.io for the interactive diagram.

```
                    R1 (Hub / Core)
                  10.0.0.1/32 [Lo0]
                  c7200 | Console: 5001
                  /              \
     Fa0/0 (.1) /                \ Fa1/0 (.1)
    10.12.0.0/30                  10.13.0.0/30
     Fa0/0 (.2) \                / Fa0/0 (.2)
                  \              /
         R2 (Branch A)      R3 (Branch B)
       10.0.0.2/32 [Lo0]  10.0.0.3/32 [Lo0]
       c3725 | Port: 5002  c3725 | Port: 5003
                  \              /
       Fa0/1 (.1)  \            / Fa0/1 (.2)
                    10.23.0.0/30
```

---

## 3. Hardware & Environment Specifications

### Device Platform Summary

| Device | Platform | Role | RAM | IOS Image |
|---|---|---|---|---|
| R1 | c7200 | Hub / Core | 512 MB | c7200-adventerprisek9-mz.153-3.XB12.image |
| R2 | c3725 | Branch A | 256 MB | c3725-adventerprisek9-mz.124-15.T14.image |
| R3 | c3725 | Branch B | 256 MB | c3725-adventerprisek9-mz.124-15.T14.image |

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

---

## 4. Base Configuration

The initial configuration loaded by `setup_lab.py` provides:

- ✅ Hostnames (`R1`, `R2`, `R3`)
- ✅ `no ip domain-lookup`
- ✅ All interface IP addresses
- ✅ Interface descriptions
- ✅ All physical interfaces in **up/up** state

**Not pre-configured (your task):**
- ❌ EIGRP process
- ❌ Network statements
- ❌ `no auto-summary`

Verify the base state before starting:
```
R1# show ip interface brief
R1# ping 10.12.0.2      ! Should succeed (directly connected)
R1# ping 10.0.0.2       ! Should FAIL (no routing protocol yet)
```

---

## 5. Lab Challenge: Core Implementation

> Complete each objective in order. Verify each before moving to the next.

### Objective 1 — Configure EIGRP AS 100 on R1

Enable EIGRP classic mode and advertise all connected networks on R1:
- Loopback0: `10.0.0.1/32`
- FastEthernet0/0: `10.12.0.0/30`
- FastEthernet1/0: `10.13.0.0/30`
- Disable auto-summary

### Objective 2 — Configure EIGRP AS 100 on R2

Enable EIGRP and advertise all connected networks on R2:
- Loopback0: `10.0.0.2/32`
- FastEthernet0/0: `10.12.0.0/30`
- FastEthernet0/1: `10.23.0.0/30`
- Disable auto-summary

### Objective 3 — Configure EIGRP AS 100 on R3

Enable EIGRP and advertise all connected networks on R3:
- Loopback0: `10.0.0.3/32`
- FastEthernet0/0: `10.13.0.0/30`
- FastEthernet0/1: `10.23.0.0/30`
- Disable auto-summary

### Objective 4 — Verify Full Adjacency and Reachability

Confirm:
- R1 shows 2 EIGRP neighbors (R2 and R3)
- R2 shows 2 EIGRP neighbors (R1 and R3)
- R3 shows 2 EIGRP neighbors (R1 and R2)
- All loopback interfaces reachable from any router via EIGRP

### Objective 5 — Troubleshooting Practice

Work through each fault scenario from `scripts/fault-injection/`. For each:
1. Inject the fault: `python3 inject_scenario_0N.py`
2. Observe symptoms without looking at the solution
3. Diagnose and fix using only `show` commands
4. Restore: `python3 apply_solution.py`

---

## 6. Verification & Analysis

### After Objective 1–3: Check Adjacencies

Run on R1:
```
R1# show ip eigrp neighbors
```
Expected output:
```
EIGRP-IPv4 Neighbors for AS(100)
H   Address         Interface       Hold Uptime   SRTT   RTO  Q  Seq
                                    (sec)         (ms)       Cnt Num
1   10.13.0.2       Fa1/0             14 00:02:15   10   200  0  7
0   10.12.0.2       Fa0/0             11 00:02:30   10   200  0  6
```
> Both R2 and R3 appear with non-zero Uptime and Hold timer > 0.

### After Objective 4: Verify Routing Table

```
R1# show ip route eigrp
```
Expected output:
```
      10.0.0.0/8 is variably subnetted
D        10.0.0.2/32 [90/156160] via 10.12.0.2, Fa0/0
D        10.0.0.3/32 [90/156160] via 10.13.0.2, Fa1/0
D        10.23.0.0/30 [90/30720] via 10.12.0.2, Fa0/0
                      [90/30720] via 10.13.0.2, Fa1/0
```
> EIGRP routes marked `D`. Equal-cost load balancing on 10.23.0.0/30 is expected.

### End-to-End Reachability Test

```
R1# ping 10.0.0.2 source 10.0.0.1
R1# ping 10.0.0.3 source 10.0.0.1
R2# ping 10.0.0.3 source 10.0.0.2
```
All pings should return `!!!!!`.

### Topology Table Inspection

```
R1# show ip eigrp topology
```
Confirm every prefix shows `P` (Passive / stable), Successor listed, and at least one path via each neighbor.

---

## 7. Verification Cheatsheet

| Command | Purpose |
|---|---|
| `show ip eigrp neighbors` | Confirm neighbor adjacencies and hold timers |
| `show ip eigrp neighbors detail` | K-values, AS number, hold time per neighbor |
| `show ip route eigrp` | EIGRP-learned routes in routing table |
| `show ip eigrp topology` | Full topology table — successors, FD, RD |
| `show ip eigrp topology all-links` | All paths, including non-feasible |
| `show ip eigrp interfaces` | EIGRP-enabled interfaces and Hello/hold timers |
| `show ip eigrp interfaces detail` | Passive interface status per interface |
| `show run \| section eigrp` | Running config — EIGRP process and network statements |
| `debug eigrp packets hello` | Live Hello packet exchange (use cautiously) |
| `ping <ip> source <ip>` | End-to-end reachability test |

---

## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these steps first!

### Objective 1 & 2 & 3: Configure EIGRP on All Routers

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1
router eigrp 100
 network 10.0.0.1 0.0.0.0
 network 10.12.0.0 0.0.0.3
 network 10.13.0.0 0.0.0.3
 no auto-summary
```

</details>

<details>
<summary>Click to view R2 Configuration</summary>

```bash
! R2
router eigrp 100
 network 10.0.0.2 0.0.0.0
 network 10.12.0.0 0.0.0.3
 network 10.23.0.0 0.0.0.3
 no auto-summary
```

</details>

<details>
<summary>Click to view R3 Configuration</summary>

```bash
! R3
router eigrp 100
 network 10.0.0.3 0.0.0.0
 network 10.13.0.0 0.0.0.3
 network 10.23.0.0 0.0.0.3
 no auto-summary
```

</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
show ip eigrp neighbors
show ip route eigrp
show ip eigrp topology
ping 10.0.0.2 source 10.0.0.1
ping 10.0.0.3 source 10.0.0.1
```

</details>

---

### Troubleshooting Scenario 1: AS Number Mismatch (Target: R2)

**Symptom:** R2 has no EIGRP neighbors. R1 and R3 are missing routes to R2.

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! On R2 — check neighbors (expect empty list)
R2# show ip eigrp neighbors

! Check running config — spot the wrong AS number
R2# show run | section eigrp
! Look for: router eigrp 200  ← incorrect, should be 100

! Check R1's neighbors — R2 is missing
R1# show ip eigrp neighbors
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R2 — remove wrong AS, restore correct one
R2(config)# no router eigrp 200
R2(config)# router eigrp 100
R2(config-router)# network 10.0.0.2 0.0.0.0
R2(config-router)# network 10.12.0.0 0.0.0.3
R2(config-router)# network 10.23.0.0 0.0.0.3
R2(config-router)# no auto-summary

! Verify adjacency restores within 15 seconds
R2# show ip eigrp neighbors
```

</details>

---

### Troubleshooting Scenario 2: Passive Interface (Target: R1)

**Symptom:** R1-R2 EIGRP adjacency is down. R2 cannot reach R3 via R1.

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! On R1 — check interface EIGRP state
R1# show ip eigrp interfaces
! Look for: Fa0/0 listed as passive (will not appear in output if passive)

R1# show ip eigrp interfaces detail
! Look for: "Passive interface" flag on Fa0/0

! Confirm in running config
R1# show run | section eigrp
! Look for: passive-interface FastEthernet0/0
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R1 — remove the passive restriction
R1(config)# router eigrp 100
R1(config-router)# no passive-interface FastEthernet0/0

! Verify adjacency with R2 restores
R1# show ip eigrp neighbors
```

</details>

---

### Troubleshooting Scenario 3: Missing Network Statement (Target: R3)

**Symptom:** R3-R2 adjacency drops. Subnet 10.23.0.0/30 disappears from R1 and R2 routing tables.

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! On R3 — check which interfaces are EIGRP-enabled
R3# show ip eigrp interfaces
! Fa0/1 (10.23.0.2) will NOT appear — not matched by any network statement

! Check routing table on R1 — missing 10.23.0.0/30
R1# show ip route eigrp

! Check running config on R3
R3# show run | section eigrp
! Look for: missing "network 10.23.0.0 0.0.0.3"
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R3 — add the missing network statement
R3(config)# router eigrp 100
R3(config-router)# network 10.23.0.0 0.0.0.3

! Verify Fa0/1 now appears in EIGRP interfaces
R3# show ip eigrp interfaces

! Verify R3-R2 adjacency restores
R3# show ip eigrp neighbors
```

</details>

---

## 9. Lab Completion Checklist

- [ ] EIGRP AS 100 configured on R1, R2, and R3
- [ ] `no auto-summary` present on all routers
- [ ] R1 shows 2 EIGRP neighbors (R2 via Fa0/0, R3 via Fa1/0)
- [ ] R2 shows 2 EIGRP neighbors (R1 via Fa0/0, R3 via Fa0/1)
- [ ] R3 shows 2 EIGRP neighbors (R1 via Fa0/0, R2 via Fa0/1)
- [ ] `show ip route eigrp` on R1 shows Lo0 routes for R2 and R3
- [ ] `ping 10.0.0.2 source 10.0.0.1` from R1 succeeds
- [ ] `ping 10.0.0.3 source 10.0.0.1` from R1 succeeds
- [ ] `ping 10.0.0.3 source 10.0.0.2` from R2 succeeds
- [ ] Completed Troubleshooting Scenario 1 (AS Mismatch)
- [ ] Completed Troubleshooting Scenario 2 (Passive Interface)
- [ ] Completed Troubleshooting Scenario 3 (Missing Network Statement)

---

## 10. Automated Fault Injection (Optional)

Fault injection scripts are in `scripts/fault-injection/`. See the `README.md` in that directory for usage.

```bash
# Prerequisites
pip install netmiko

# Run setup (push initial configs to all routers)
python3 setup_lab.py

# Inject a fault scenario
python3 scripts/fault-injection/inject_scenario_01.py

# Restore after completing a scenario
python3 scripts/fault-injection/apply_solution.py
```

| Script | Fault | Target |
|---|---|---|
| `inject_scenario_01.py` | AS Number Mismatch (100 → 200) | R2 |
| `inject_scenario_02.py` | Passive Interface on Fa0/0 | R1 |
| `inject_scenario_03.py` | Missing network statement for 10.23.0.0/30 | R3 |
| `apply_solution.py` | Restore all devices to correct config | R1, R2, R3 |
