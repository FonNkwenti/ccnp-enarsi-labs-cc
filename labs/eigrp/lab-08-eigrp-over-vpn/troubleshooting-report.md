# Troubleshooting Report — EIGRP over GRE Tunnel Adjacency Failure

**Lab:** EIGRP Lab 08 — EIGRP over VPN Tunnel
**Date:** 2026-02-20
**Symptom:** EIGRP AS 100 adjacency not forming between R1 and R6 over Tunnel8

---

## Phase I — Problem Definition

**Precise fault statement:**
R1 (`Tu8: 172.16.16.1`) and R6 (`Tu8: 172.16.16.2`) fail to establish an EIGRP AS 100 neighbor relationship over the GRE tunnel, despite both tunnel endpoints being up and reachable.

**Scope:** R1 ↔ R6 only. R1 ↔ R2 EIGRP adjacency is unaffected.

---

## Phase II — Methodology

**Selected: Divide and Conquer**

Rationale: This is a multi-layer problem spanning physical underlay (Gi3/0), GRE tunnel overlay (Tunnel8), and EIGRP control plane. Dividing the stack into layers and eliminating each from the bottom up is the most efficient approach.

Layers checked (bottom → top):

```
[ Layer 3 — EIGRP Control Plane ]  ← fault lives here
[ Layer 2 — GRE Tunnel Overlay  ]
[ Layer 1 — IP Underlay Gi3/0   ]
```

---

## Phase III — Diagnostic Log

### Step 1 — Interface Status

**Command:** `show ip interface brief`

| Device | Interface | IP Address | Status | Protocol |
|--------|-----------|------------|--------|----------|
| R1 | GigabitEthernet3/0 | 10.0.16.1 | up | up |
| R1 | Tunnel8 | 172.16.16.1 | up | up |
| R6 | GigabitEthernet3/0 | 10.0.16.2 | up | up |
| R6 | Tunnel8 | 172.16.16.2 | up | up |

**Conclusion:** All interfaces are up. Layer 1 eliminated as a cause.

---

### Step 2 — IP Underlay Reachability

**Command:** `ping 10.0.16.2` (from R1), `ping 10.0.16.1` (from R6)

```
R1# ping 10.0.16.2
Success rate is 100 percent (5/5), round-trip min/avg/max = 20/56/92 ms

R6# ping 10.0.16.1
Success rate is 100 percent (5/5), round-trip min/avg/max = 16/54/92 ms
```

**Conclusion:** Underlay (Gi3/0 ↔ Gi3/0) is fully functional. Eliminated as a cause.

---

### Step 3 — GRE Tunnel Reachability

**Command:** `ping 172.16.16.2 source 172.16.16.1` (from R1)

```
R1# ping 172.16.16.2 source 172.16.16.1
Packet sent with a source address of 172.16.16.1
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 92/95/96 ms

R6# ping 172.16.16.1 source 172.16.16.2
Packet sent with a source address of 172.16.16.2
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 96/101/112 ms
```

**Conclusion:** GRE tunnel is operational end-to-end. IP packets traverse the tunnel correctly. Eliminated as a cause.
**Implication:** The fault is isolated to the EIGRP control plane.

---

### Step 4 — EIGRP Neighbor Table

**Command:** `show ip eigrp neighbors`

```
R1# show ip eigrp neighbors
EIGRP-IPv4 Neighbors for AS(100)
H   Address         Interface   Hold  Uptime    SRTT  RTO   Q  Seq
0   10.0.12.2       Fa1/0       152   00:49:37  53    318   0  38

R6# show ip eigrp neighbors
EIGRP-IPv4 Neighbors for AS(100)
(empty)
```

**Conclusion:** R1 has R2 as a neighbor on Fa1/0 but no neighbor on Tu8. R6 has no neighbors at all.

---

### Step 5 — EIGRP Active Interfaces

**Command:** `show ip eigrp interfaces`

```
R1# show ip eigrp interfaces
EIGRP-IPv4 Interfaces for AS(100)
Interface    Peers  Xmit Queue  Mean  Pacing Time  Multicast   Pending
Fa1/0          1      0/0        53    0/16          208          0
Tu8            0      0/0         0    6/233         621          0
                ↑
                Tunnel8 IS active in EIGRP on R1, but has 0 peers

R6# show ip eigrp interfaces
EIGRP-IPv4 Interfaces for AS(100)
Interface    Peers  Xmit Queue  Mean  Pacing Time  Multicast   Pending
Lo0            0      0/0         0    0/0            0          0
                ↑
                Only Loopback0 is active — Tunnel8 is NOT in EIGRP on R6
```

**Conclusion:** This is the smoking gun. R1 is sending EIGRP hellos out Tu8. R6 has no EIGRP process running on Tunnel8 at all.

---

### Step 6 — EIGRP Configuration Comparison

**Command:** `show running-config | section router eigrp`

```
R1# show running-config | section router eigrp
router eigrp 100
 network 1.1.1.1 0.0.0.0
 network 10.0.12.0 0.0.0.3
 network 172.16.16.0 0.0.0.3   ← Tunnel8 subnet is covered ✅
 ...

R6# show running-config | section router eigrp
router eigrp 100
 network 6.6.6.6 0.0.0.0       ← only Loopback0 is covered ❌
                                   172.16.16.0/30 is MISSING
```

**Conclusion:** Root cause confirmed.

---

## Root Cause Analysis

R6's `router eigrp 100` configuration is **incomplete**. The `network` statement covering the Tunnel8 subnet (`172.16.16.0/30`) is absent.

Without a matching `network` statement, IOS will not:
- Activate EIGRP on Tunnel8
- Send EIGRP Hello packets out Tunnel8
- Accept EIGRP Hello packets received on Tunnel8

R1 is correctly sending Hellos out Tu8 every `Hello Interval` seconds, but R6 silently discards them because Tunnel8 is not an EIGRP-enabled interface. The adjacency can never form.

The underlay and tunnel are **not the problem** — everything below the EIGRP control plane is working perfectly.

---

## What to Fix

You need to add a single configuration element to **R6's** EIGRP process.

**Hint:** Look at how R1's `router eigrp 100` includes the tunnel subnet and apply the same logic to R6. The subnet to cover is `172.16.16.0/30`.

**Verification commands to confirm your fix worked:**

```
! On R6 — Tunnel8 should appear here after your fix
show ip eigrp interfaces

! On both R1 and R6 — should show a neighbor after adjacency forms
show ip eigrp neighbors

! Confirm R6 loopback is reachable from R1 via EIGRP
R1# show ip route 6.6.6.6
```

**Expected adjacency output after fix:**
```
R1# show ip eigrp neighbors
EIGRP-IPv4 Neighbors for AS(100)
H   Address         Interface   Hold  Uptime  SRTT  RTO   Q  Seq
0   10.0.12.2       Fa1/0       ...
1   172.16.16.2     Tu8         ...   ← new neighbor over the tunnel
```

---

## Lessons Learned

1. **EIGRP `network` statements activate interfaces, not just advertise prefixes.** If an interface's subnet is not matched by a `network` statement, EIGRP will not send or receive hellos on it — regardless of whether the interface itself is up.

2. **Always use `show ip eigrp interfaces` early in GRE/tunnel troubleshooting.** It immediately tells you which interfaces EIGRP is actually running on, which is faster than chasing tunnel or underlay issues.

3. **Confirm tunnel reachability before blaming EIGRP.** Pinging across the tunnel (`source` the tunnel IP) proves the GRE encapsulation and underlay are working, cleanly separating the transport problem from the routing protocol problem.

4. **Divide and Conquer by layer** saves time: underlay → tunnel → control plane. In this case, two layers were eliminated in under 5 commands.
