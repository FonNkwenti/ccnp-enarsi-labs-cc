# EIGRP Lab 06 — Stub Routing: Branch Router Protection

**Exam:** CCNP ENARSI 300-410
**Difficulty:** Intermediate
**Estimated Time:** 60 minutes

---

## 1. Concepts & Skills Covered

### Blueprint Coverage

| Blueprint ID | Topic |
|---|---|
| 1.9.d | EIGRP stub routing |

### Key Concepts

**EIGRP Stub Router**

A stub router is a branch or edge router that should never be used as a transit path between other routers. By configuring `eigrp stub`, the router:

1. **Advertises only specific route types** (not all learned routes)
2. **Receives a query from core routers saying "don't query me"** — core routers will not send DUAL queries to a stub router
3. **Reduces DUAL recalculation burden** on the network — stub routers are not involved in reconvergence

**Stub Keywords**

```
router eigrp AS
 eigrp stub [keyword] [keyword] ...
```

Common keywords:
- **connected:** Advertise only directly connected subnets
- **summary:** Advertise only summary routes (created by `ip summary-address`)
- **static:** Advertise only static routes redistributed into EIGRP
- **receive-only:** Advertise nothing (only receive routes from neighbors)

**Configuration Examples**

```
! Stub router that advertises only its connected subnets and summary routes
eigrp stub connected summary

! Stub router that receives routes but advertises nothing (silent fail-safe)
eigrp stub receive-only

! Stub router that advertises connected, summary, and static routes
eigrp stub connected summary static
```

**Default Behavior**

By default, a router advertises all learned routes:
```
eigrp stub connected summary
```

This is the implicit default. To override, you must explicitly configure `eigrp stub` with different keywords.

**Impact on Neighbor Relationships**

When a router is configured as a stub:
1. Other routers learn it is a stub from Hello packets
2. Core routers suppress DUAL queries to the stub router
3. The stub router still receives all routes from neighbors
4. The stub router still sends full updates to neighbors (only specific route types)

---

## 2. Topology & Scenario

### Enterprise Scenario

Acme Corp has deployed a branch office router (R4) that connects only to the hub (R1). R4 should never become a transit router — it should only advertise its own subnets and receive routes from the hub. By configuring R4 as a stub router, you ensure that:

1. R4 is not queried during EIGRP reconvergence (reducing failover time on core routers)
2. Only necessary routes are advertised from R4
3. R4 cannot inadvertently become a transit path between other branches

This lab extends the three-router triangle (Labs 01–05) with a fourth router (R4) connected only to R1. You will configure R4 as a stub router and verify it behaves correctly.

### Topology Reference

The three-router triangle continues, with a new link added:
- **R1** (Hub): Now has a fourth interface (Fa1/1) connecting to R4
- **R2** (Branch A): No changes
- **R3** (Branch B): No changes
- **R4** (New Stub/Edge): 10.14.0.2/30, Loopback0: 10.0.0.4/32

```
              ┌─────────────────────────┐
              │           R1            │
              │      (Hub / Core)       │
              │   Lo0: 10.0.0.1/32      │
              └──────┬───────────┬──────┬───────────┐
           Fa0/0     │           │     Fa1/0      Fa1/1
     10.12.0.1/30    │           │   10.13.0.1/30 10.14.0.1/30
                     │           │                │
     10.12.0.2/30    │           │   10.13.0.2/30 │ 10.14.0.2/30
           Fa0/0     │           │     Fa0/0      │
     ┌───────────────┘           └───────────┐    │
     │                                       │    │
┌────┴──────────────┐           ┌────────────┴────┐
│       R2          │           │       R3        │
│   (Branch A)      │           │   (Branch B)    │
│ Lo0: 10.0.0.2/32  │           │ Lo0: 10.0.0.3/32│
└─────────┬─────────┘           └─────────┬───────┘
      Fa0/1│                              │Fa0/1
10.23.0.1/30│                            │10.23.0.2/30
            └────────────────────────────┘
                     10.23.0.0/30

              ┌──────────────────┐
              │       R4         │
              │  (Stub/Edge)     │
              │ Lo0: 10.0.0.4/32 │
              └──────────────────┘
```

> Open `topology.drawio` in Draw.io for the interactive diagram.

---

## 3. Hardware & Environment Specifications

### Device Platform Summary

| Device | Platform | Role | RAM | IOS Image |
|---|---|---|---|---|
| R1 | c7200 | Hub / Core | 512 MB | c7200-adventerprisek9-mz.153-3.XB12.image |
| R2 | c3725 | Branch A | 256 MB | c3725-adventerprisek9-mz.124-15.T14.image |
| R3 | c3725 | Branch B | 256 MB | c3725-adventerprisek9-mz.124-15.T14.image |
| R4 | c3725 | Stub/Edge | 256 MB | c3725-adventerprisek9-mz.124-15.T14.image |

### IP Address Reference

| Device | Interface | IPv4 Address |
|---|---|---|
| R1 | Loopback0 | 10.0.0.1/32 |
| R1 | FastEthernet1/1 | 10.14.0.1/30 |
| R4 | Loopback0 | 10.0.0.4/32 |
| R4 | FastEthernet0/0 | 10.14.0.2/30 |

### Cabling Table

| Link ID | Source | Interface | Target | Interface | Subnet |
|---|---|---|---|---|---|
| L1 | R1 | Fa0/0 | R2 | Fa0/0 | 10.12.0.0/30 |
| L2 | R1 | Fa1/0 | R3 | Fa0/0 | 10.13.0.0/30 |
| L3 | R2 | Fa0/1 | R3 | Fa0/1 | 10.23.0.0/30 |
| L4 | R1 | Fa1/1 | R4 | Fa0/0 | 10.14.0.0/30 |

### Console Access Table

| Device | Console Port | Connection Command |
|---|---|---|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |
| R4 | 5004 | `telnet 127.0.0.1 5004` |

---

## 4. Base Configuration

The initial configuration for Lab 06 is the **exact working solution from Lab 05** — R1, R2, and R3 are fully configured with EIGRP, summarization, and proper routing. R4 is added to the topology with only IP addressing (Loopback0 and Fa0/0); no EIGRP configuration is present.

**Pre-configured (from Lab 05):**
- ✅ EIGRP AS 100 on R1, R2, R3 (with summarization)
- ✅ All three routers have neighbor adjacencies
- ✅ Full IPv4 reachability in the triangle
- ✅ R4 loopback0 and Fa0/0 IP addresses configured

**Not pre-configured (your task):**
- ❌ EIGRP process on R4
- ❌ Network statements on R4
- ❌ Stub configuration on R4
- ❌ EIGRP on R1 Fa1/1 (toward R4)

Verify the base state:
```
R4# show ip interface brief
! Should show Lo0 and Fa0/0 up/up with correct addresses

R1# show ip eigrp interfaces
! Fa1/1 should NOT appear yet

R1# show ip eigrp neighbors
! Should show only R2 and R3 (R4 not yet a neighbor)
```

---

## 5. Lab Challenge: Core Implementation

> Complete each objective in order. Verify each before moving to the next.

### Objective 1 — Enable EIGRP on R1 Fa1/1 (Link to R4)

On R1, add the link to R4 to EIGRP:

```
router eigrp 100
 network 10.14.0.0 0.0.0.3
```

Verify the link is EIGRP-enabled:
```
R1# show ip eigrp interfaces
! Fa1/1 should appear

R1# show ip eigrp neighbors
! R4 is not yet listed (R4 has no EIGRP)
```

### Objective 2 — Enable EIGRP on R4 (Non-Stub First)

On R4, enable EIGRP AS 100 with its loopback and link to R1:

```
router eigrp 100
 network 10.0.0.4 0.0.0.0
 network 10.14.0.0 0.0.0.3
 no auto-summary
```

Verify R4 forms an adjacency with R1:
```
R4# show ip eigrp neighbors
! R1 should appear

R1# show ip eigrp neighbors
! R4 (10.14.0.2) should now appear
```

### Objective 3 — Verify R4 Learns All Routes (Before Stub Configuration)

Before configuring R4 as a stub, verify it learns all routes from the network:

```
R4# show ip route eigrp
```

Expected: R4 should learn routes for:
- 10.0.0.1/32 (R1 Loopback)
- 10.0.0.2/32 (R2 Loopback)
- 10.0.0.3/32 (R3 Loopback)
- 10.12.0.0/30 (R1-R2 link)
- 10.13.0.0/30 (R1-R3 link)
- 10.23.0.0/30 (R2-R3 link)
- 172.16.20.0/23 (R2 summary)
- 172.16.30.0/23 (R3 summary)

### Objective 4 — Configure R4 as Stub Router

On R4, configure it as a stub router that advertises only connected subnets and summary routes:

```
router eigrp 100
 eigrp stub connected summary
```

This command:
- Tells core routers "I am a stub, do not query me"
- Limits R4's advertisements to only connected and summary routes
- Allows R4 to still receive all routes from neighbors

### Objective 5 — Verify Stub Configuration and Neighbor Awareness

Verify R4 is recognized as a stub by checking the neighbor detail on R1:

```
R1# show ip eigrp neighbors detail
! Look for neighbor 10.14.0.2 and verify it shows as a stub
! Expected line: "Stub router"
```

Also verify on R4:
```
R4# show ip eigrp neighbors detail
! Should show R1 as a neighbor (normal, non-stub)
```

### Objective 6 — Verify R4 Only Advertises Connected and Summary Routes

Examine what R4 advertises toward the network. From a non-stub router (e.g., R2), verify that routes to other branches are NOT learned via R4:

```
R2# show ip route
! R3 loopback (10.0.0.3) should still route via R1, not R4
! The route to R4 itself (10.0.0.4) should appear via R1

R1# show ip route eigrp | include 10.0.0.4
! R4's loopback should be reachable via Fa1/1 (direct connection)
```

Check what R1 learns from R4:
```
R1# show ip eigrp topology
! Should see only 10.0.0.4/32 as a route learned from R4
```

### Objective 7 — Verify R4 Cannot Be Used as Transit

To confirm R4 is truly a stub, verify that core routers do not use R4 as a transit path. For example, if you were to advertise R2's subnets from R4, R3 would still reach R2 directly through R1, not via R4.

Test this by simulating a traceroute from R1:
```
R1# show ip eigrp neighbors
! Note that R4 is marked as Stub

R1# show ip route eigrp 10.0.0.3
! Should go via R3 directly (Fa1/0), not via R4
```

---

## 6. Verification & Analysis

### After Objective 1–2: Adjacency Established

Once EIGRP is enabled on both R1 Fa1/1 and R4, verify adjacency:

```
R1# show ip eigrp neighbors
```

Expected output (abbreviated):
```
EIGRP-IPv4 Neighbors for AS(100)
H   Address         Interface       Hold Uptime   SRTT   RTO  Q  Seq
                                    (sec)         (ms)       Cnt Num
2   10.14.0.2       Fa1/1             13 00:00:45   10   200  0  3
1   10.13.0.2       Fa1/0             12 00:01:23   10   200  0  7
0   10.12.0.2       Fa0/0             14 00:01:45   10   200  0  6
```

All three neighbors (including R4) should be present.

### After Objective 3: Routes Learned Before Stub

Before the stub configuration, R4 should learn all routes:

```
R4# show ip route eigrp
```

Expected output:
```
      10.0.0.0/8 is variably subnetted, 7 subnets, 2 masks
D        10.0.0.1/32 [90/156160] via 10.14.0.1, Fa0/0
D        10.0.0.2/32 [90/173120] via 10.14.0.1, Fa0/0
D        10.0.0.3/32 [90/158720] via 10.14.0.1, Fa0/0
D        10.12.0.0/30 [90/30720] via 10.14.0.1, Fa0/0
D        10.13.0.0/30 [90/30720] via 10.14.0.1, Fa0/0
D        10.23.0.0/30 [90/30720] via 10.14.0.1, Fa0/0
D        172.16.20.0/23 [90/33280] via 10.14.0.1, Fa0/0
D        172.16.30.0/23 [90/33280] via 10.14.0.1, Fa0/0
```

All 8 external routes learned.

### After Objective 4–5: Stub Configuration Active

After configuring `eigrp stub connected summary`:

```
R1# show ip eigrp neighbors detail 10.14.0.2
```

Expected output includes:
```
Neighbor Address: 10.14.0.2
Interface: FastEthernet1/1
Uptime: 00:01:15
SRTT: 15 msec, RTO: 45 msec
Q Cnt: 0
Seq Num: 8
Stub router
```

The key indicator is "Stub router" in the output.

### After Objective 6: Limited Route Advertisement

After stub configuration, verify R4 still learns all routes but only advertises connected/summary:

```
R4# show ip route eigrp
! Should still show all 8 routes (R4 receives from R1)
```

But check what other routers see:

```
R2# show ip route eigrp 10.0.0.4
! R4's loopback should be reachable via R1, not directly from R4
! Next-hop should be 10.12.0.1 (R1), not from any other direction
```

And verify on R1:

```
R1# show ip eigrp topology | include 10.0.0.4
! Should show: "P 10.0.0.4/32, 1 successors, FD is..."
! Next-hop: "via 10.14.0.2 (neighbor metric/RD)"
! R4 should only advertise its own loopback, not learned routes
```

---

## 7. Verification Cheatsheet

| Command | Purpose |
|---|---|
| `show ip eigrp neighbors detail` | Verify stub status of neighbors |
| `show ip eigrp interfaces` | Verify which interfaces are EIGRP-enabled |
| `show ip route eigrp` | Verify routes learned (should be comprehensive) |
| `show ip eigrp topology` | Verify what routes are in the topology database |
| `show run \| section eigrp` | Verify eigrp stub command is configured |

---

## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these steps first!

### R1 Configuration: Enable EIGRP on Fa1/1

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1 — Add Fa1/1 to EIGRP (link to R4)
router eigrp 100
 network 10.14.0.0 0.0.0.3
```

</details>

### R4 Configuration: EIGRP + Stub

<details>
<summary>Click to view R4 Configuration</summary>

```bash
! R4 — Enable EIGRP and configure stub
router eigrp 100
 network 10.0.0.4 0.0.0.0
 network 10.14.0.0 0.0.0.3
 no auto-summary
 eigrp stub connected summary
```

</details>

### Verification Commands

<details>
<summary>Click to view Key Verification Commands</summary>

```bash
! Verify R4 is a stub neighbor (on R1)
show ip eigrp neighbors detail

! Verify R4 learns all routes despite being a stub
show ip route eigrp

! Verify R4 topology database
show ip eigrp topology

! Verify stub command is configured
show run | section eigrp
```

</details>

---

## 9. Troubleshooting Scenarios

Each ticket simulates a real-world fault related to stub routing. Inject the fault first, then diagnose using only show commands.

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

### Ticket 1 — Stub Configuration Leaking Transit Routes

After configuring R4 as a stub, the network team observes that R4 is still advertising routes learned from other branches. R2 is receiving routes to R3 via R4, which is incorrect — R2 should reach R3 only via R1.

**Inject:** `python3 scripts/fault-injection/inject_scenario_01.py`

**Symptoms:**
- `show ip route 10.0.0.3` on R2 shows next-hop via R4 (10.14.0.2)
- R4 is advertising routes it should not (learned, not connected)
- `show ip eigrp neighbors detail` on R1 shows R4 as a stub, but traffic is still using it as transit

**Success criteria:**
- R4 advertises only its own loopback (10.0.0.4/32) and any configured summaries
- R2 reaches R3 via R1, not via R4
- Stub configuration is correct and honored

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Check what R2 sees
R2# show ip route 10.0.0.3
! If next-hop is 10.23.0.2 (R3) or 10.12.0.1 (R1), this is correct
! If next-hop is 10.14.x.x (R4), this indicates leaking

! Check R4's configuration
R4# show run | section eigrp
! Look for: "eigrp stub connected summary"
! If missing or different, the stub is not configured correctly

! Check what R4 is advertising (check via traceback)
R4# show ip eigrp topology | include advertise
! Only 10.0.0.4/32 should be listed as sourced by R4
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R4 — Verify or re-configure stub
R4(config)# router eigrp 100
R4(config-router)# eigrp stub connected summary

! Verify the configuration
R4# show run | section eigrp
! Should show: "eigrp stub connected summary"

! Clear neighbors to force re-sync
R4# clear ip eigrp neighbors

! Verify R2 no longer sees R3 via R4
R1# show ip eigrp neighbors detail
! R4 should be marked as "Stub router"

! Verify on R2
R2# show ip route 10.0.0.3
! Should show next-hop via R1 (10.12.0.1 or 10.23.0.2), not R4
```

</details>

---

### Ticket 2 — Stub Router Losing Routes to Core

After a configuration change, R4 can no longer reach destinations learned from R1 (e.g., R2's loopback). R4 still has an adjacency with R1, but the routing table is incomplete.

**Inject:** `python3 scripts/fault-injection/inject_scenario_02.py`

**Symptoms:**
- `show ip route eigrp` on R4 shows fewer than expected routes (missing 10.0.0.2, 10.0.0.3, etc.)
- `show ip eigrp neighbors` on R4 shows R1 as a neighbor
- R4 can ping R1 (10.14.0.1) but not R1's loopback (10.0.0.1)
- `show ip eigrp neighbors detail` on R1 shows "Stub router" for R4

**Success criteria:**
- R4 receives all routes from R1 (should learn 10.0.0.1, 10.0.0.2, 10.0.0.3, etc.)
- Reachability to all core and branch loopbacks restored

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Check R4's routing table
R4# show ip route eigrp
! Should show entries for all three loopbacks and links

! Count how many EIGRP routes R4 has vs. expected
! Expected: at least 7-8 routes (3 loopbacks + 3 links + 2 summaries)

! Check R4's EIGRP interfaces
R4# show ip eigrp interfaces
! Fa0/0 should be listed

! Check if R4 is configured as passive on Fa0/0
R4# show run | section eigrp
! Look for: "passive-interface FastEthernet0/0" (should NOT exist)

! The problem may be that Fa0/0 is passive, preventing R4 from receiving full updates
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R4 — Ensure Fa0/0 is not passive
R4(config)# router eigrp 100
R4(config-router)# no passive-interface FastEthernet0/0

! Verify the command is removed
R4# show run | section eigrp
! Should NOT show "passive-interface FastEthernet0/0"

! Clear neighbors to force full update exchange
R4# clear ip eigrp neighbors

! Verify routes are now learned
R4# show ip route eigrp
! Should now show all expected routes

! Test reachability
R4# ping 10.0.0.1 source 10.0.0.4
! Should succeed
```

</details>

---

### Ticket 3 — Stub Router Receiving Queries (Should Not Happen)

During a network outage, R4 receives DUAL query packets from R1. This should not happen — stub routers should not be queried. This indicates R4's stub configuration is not being recognized or propagated correctly.

**Inject:** `python3 scripts/fault-injection/inject_scenario_03.py`

**Symptoms:**
- During a link failure (e.g., R1-R2 link goes down), R1 sends queries to R4
- R4 responds with query replies, adding latency to EIGRP reconvergence
- `show ip eigrp neighbors detail` on R1 does NOT show "Stub router" for R4
- R4's configuration appears correct

**Success criteria:**
- R1 recognizes R4 as a stub and does not send queries to it
- EIGRP reconvergence is faster (only involves R1, R2, R3)
- Stub neighbor flag is visible on R1

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! On R1 — Check neighbor detail for R4
R1# show ip eigrp neighbors detail 10.14.0.2
! Look for: "Stub router" keyword
! If NOT present, R1 doesn't see R4 as a stub

! On R4 — Verify stub is configured
R4# show run | section eigrp
! Look for: "eigrp stub connected summary"

! The issue may be that:
! 1. Stub was not configured on R4
! 2. Stub was configured but neighbors need to be reset to learn the new status
! 3. The IOS version doesn't support stub (unlikely in modern releases)
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R4 — Ensure stub is configured
R4(config)# router eigrp 100
R4(config-router)# eigrp stub connected summary

! Clear neighbors on both R1 and R4 to force re-negotiation
R4# clear ip eigrp neighbors
R1# clear ip eigrp neighbors

! Verify on R1 that stub is now recognized
R1# show ip eigrp neighbors detail 10.14.0.2
! Should now show: "Stub router"

! During the next link failure, R1 will NOT query R4
! Only R1, R2, R3 will participate in reconvergence
```

</details>

---

### Ticket 4 — Connected Routes Not Being Advertised by Stub

R4 is configured as a stub with `eigrp stub connected summary`, but R1 is not receiving R4's loopback (10.0.0.4/32). The connectivity from the core network to R4 is missing.

**Inject:** `python3 scripts/fault-injection/inject_scenario_04.py`

**Symptoms:**
- `show ip route 10.0.0.4` on R1 returns "no route to host" or shows a direct connection only
- `show ip eigrp topology` on R1 does not include 10.0.0.4/32
- R4 has a loopback configured (10.0.0.4), but it's not in EIGRP

**Success criteria:**
- R4's loopback appears in R1's topology table
- R1 can reach 10.0.0.4/32 via EIGRP (metric shown)
- Stub configuration remains `connected summary`

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! On R4 — Check if loopback is in EIGRP
R4# show ip eigrp interfaces
! Loopback0 should NOT appear (loopbacks must be added via network statement)

! Check running config on R4
R4# show run | section eigrp
! Should include: "network 10.0.0.4 0.0.0.0"
! If missing, the loopback is not advertised

! Verify loopback exists and is up
R4# show ip interface brief | include Loopback0
! Should show Loopback0 with correct IP and up/up status
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R4 — Add the loopback to EIGRP network statements
R4(config)# router eigrp 100
R4(config-router)# network 10.0.0.4 0.0.0.0

! Verify the network statement is in the config
R4# show run | section eigrp

! Loopback0 should now be advertised as a "connected" route (because stub connected summary)
R4# show ip eigrp topology | include 10.0.0.4
! Should show: "P 10.0.0.4/32, ..." (now in topology)

! Verify on R1
R1# show ip route 10.0.0.4
! Should show: [90/XXX] via 10.14.0.2, Fa1/1 (or similar metric)
```

</details>

---

### Ticket 5 — R4 Becoming Unintended Transit Router

Despite being configured as a stub, R4 is inadvertently being used as a transit path by R2 or R3 to reach other branches. This could happen if the stub configuration is partially overridden or if routes are being redistributed.

**Inject:** `python3 scripts/fault-injection/inject_scenario_05.py`

**Symptoms:**
- `show ip route 10.0.0.3` on R2 shows next-hop via R4 (10.14.0.2)
- R4 is advertising routes it learned (e.g., 10.13.0.0/30, 10.0.0.3/32)
- `show ip eigrp neighbors detail` on R1 shows "Stub router" for R4, but traffic still uses it

**Success criteria:**
- R4 does not advertise transit routes
- R2, R3, and R1 all reach each other WITHOUT going through R4
- Stub configuration prevents R4 from becoming transit

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! On R1 — Check if R4 is advertising unauthorized routes
R1# show ip eigrp topology | grep "via 10.14"
! Should only show "via 10.14.0.2" for 10.0.0.4/32 (R4's own loopback)
! Should NOT show other routes coming from R4

! On R2 — Check routing path to R3
R2# show ip route 10.0.0.3
! Verify next-hop is NOT R4 (10.14.x.x)
! Should be R1 (10.12.0.1) or R3 (10.23.0.2)

! The issue may be:
! 1. Stub is not configured on R4
! 2. Stub is configured but has the wrong keywords
! 3. Another configuration (redistribution, static routes) is overriding stub
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R4 — Verify and reconfigure stub if needed
R4(config)# router eigrp 100
R4(config-router)# eigrp stub connected summary

! Remove any redistribution that might be advertising unauthorized routes
R4(config-router)# no redistribute <protocol>  ! (if any is configured)

! Clear neighbors on both R1 and R4
R4# clear ip eigrp neighbors
R1# clear ip eigrp neighbors

! Verify on R1 that only R4's loopback is learned from R4
R1# show ip eigrp topology | grep "via 10.14"
! Should show ONLY: "via 10.14.0.2 (...)" for 10.0.0.4/32

! Verify on R2 that R3 is not reached via R4
R2# show ip route 10.0.0.3
! Next-hop should be 10.12.0.1 (R1) or 10.23.0.2 (R3)
```

</details>

---

## 10. Lab Completion Checklist

**Concepts**
- [ ] Understand EIGRP stub routers and their purpose (prevent transit use)
- [ ] Explain the keywords: `connected`, `summary`, `static`, `receive-only`
- [ ] Understand how stub routers are identified by neighbors (via Hello packets)
- [ ] Understand that stub routers still receive all routes but advertise selectively

**Configuration**
- [ ] Add network statement on R1 for 10.14.0.0/30 (Fa1/1 toward R4)
- [ ] Configure EIGRP on R4 with loopback and link to R1
- [ ] Configure `eigrp stub connected summary` on R4
- [ ] Verify `no auto-summary` is present on R4

**Verification**
- [ ] R1 and R4 form EIGRP adjacency
- [ ] R1 shows R4 as "Stub router" in neighbor detail
- [ ] R4 learns all routes from the network (full route table)
- [ ] R4 advertises only 10.0.0.4/32 (connected loopback)
- [ ] Other routers (R2, R3) do not use R4 as a transit path
- [ ] Traceback from any router to any destination never goes through R4

**Troubleshooting**
- [ ] Ticket 1 diagnosed and resolved (stub leaking routes)
- [ ] Ticket 2 diagnosed and resolved (stub losing routes)
- [ ] Ticket 3 diagnosed and resolved (stub receiving queries)
- [ ] Ticket 4 diagnosed and resolved (connected routes not advertised)
- [ ] Ticket 5 diagnosed and resolved (unintended transit use)

**End-to-End Verification**
- [ ] All neighbors established and stable
- [ ] R1 has 3 EIGRP neighbors (R2, R3, R4)
- [ ] R4 has 1 EIGRP neighbor (R1)
- [ ] Full mesh of reachability (R1↔R2, R1↔R3, R2↔R3, R1↔R4)
- [ ] R4 cannot be used as a transit path
