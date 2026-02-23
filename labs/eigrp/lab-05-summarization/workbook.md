# EIGRP Lab 05 — Summarization: Manual Route Aggregation

**Exam:** CCNP ENARSI 300-410
**Difficulty:** Intermediate
**Estimated Time:** 75 minutes

---

## 1. Concepts & Skills Covered

### Blueprint Coverage

| Blueprint ID | Topic |
|---|---|
| 1.5 | Troubleshoot manual and auto-summarization |

### Key Concepts

**Manual Summarization**

EIGRP allows you to aggregate multiple subnets into a single summary route at the outgoing interface, reducing routing table size on downstream routers. The summary route is advertised instead of individual prefixes.

```
router eigrp AS
 interface FastEthernet X/Y
  ip summary-address eigrp AS 172.16.0.0 255.255.254.0
```

This command advertises a single 172.16.0.0/23 route that encompasses 172.16.0.0/24 through 172.16.1.0/24 and suppresses the individual subnets.

**Null0 Discard Route**

When you configure a summary, EIGRP automatically creates an internal route pointing to null0 (discard interface) for the summary route. This protects against routing loops — if a more specific subnet exists elsewhere, traffic to missing subnets in the summary block is discarded locally rather than forwarded back out the interface.

Example:
```
R2# show ip route 172.16.20.0
Routing entry for 172.16.20.0/23, supernet
  Known via "eigrp 100", distance 5, metric 28160, type internal
  Redistributed by eigrp 100
  Advertised by eigrp 100
  Routing Descriptor Blocks:
    * directly connected, via Null0
      Route metric is 28160, traffic share count is 1
```

**Summarization Black Hole**

If you summarize subnets that do not exist locally, traffic destined for those subnets will be dropped at the summary point. For example, if R2 advertises 172.16.20.0/23 but only has 172.16.20.0/24 configured, traffic to 172.16.21.0/24 will match the summary and be sent to R2, where it will be discarded.

**Auto-Summary**

In classic EIGRP, auto-summary is enabled by default and automatically summarizes routes to classful boundaries at major network changes. This causes problems with discontiguous networks:

```
network 10.0.0.0
```

Will summarize all 10.x.x.x subnets to 10.0.0.0/8 at class boundaries, potentially creating black holes.

---

## 2. Topology & Scenario

### Enterprise Scenario

Acme Corp wants to reduce the size of their routing tables by summarizing branch office subnets. Branch A (R2) has multiple server subnets (172.16.20.x and 172.16.21.x), and Branch B (R3) has similar networks (172.16.30.x and 172.16.31.x). You will add loopback interfaces to simulate these server networks and configure manual summarization on R2 and R3 to advertise a single summary route to the hub.

This lab continues from Lab 04 — EIGRP is fully configured with proper adjacencies and routing. You will now extend R2 and R3 with additional loopback interfaces and configure route summarization.

### Topology Reference

The three-router triangle from Labs 01–04 continues:
- **R1** (Hub): Receives and learns summarized routes from R2 and R3
- **R2** (Branch A): Advertises 172.16.20.0/23 (covering Lo1: 172.16.20.0/24 and Lo2: 172.16.21.0/24)
- **R3** (Branch B): Advertises 172.16.30.0/23 (covering Lo1: 172.16.30.0/24 and Lo2: 172.16.31.0/24)

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
| R2 | Loopback0 | 10.0.0.2/32 |
| R2 | Loopback1 | 172.16.20.0/24 (to be added) |
| R2 | Loopback2 | 172.16.21.0/24 (to be added) |
| R3 | Loopback0 | 10.0.0.3/32 |
| R3 | Loopback1 | 172.16.30.0/24 (to be added) |
| R3 | Loopback2 | 172.16.31.0/24 (to be added) |

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

The initial configuration for Lab 05 is the **exact working solution from Lab 04** — all three routers are running EIGRP classic mode (AS 100) with proper neighbor adjacencies and routing in place. No loopback interfaces are yet configured on R2 and R3.

**Pre-configured (from Lab 04):**
- ✅ EIGRP AS 100 on all routers
- ✅ `no auto-summary` on all routers
- ✅ All neighbor adjacencies established
- ✅ Full IPv4 reachability

**Not pre-configured (your task):**
- ❌ Loopback interfaces (Lo1, Lo2) on R2 and R3
- ❌ Network statements for new loopbacks
- ❌ Manual summarization on R2 and R3

Verify the base state:
```
R2# show ip interface brief | include Loopback
! Should show only Loopback0

R1# show ip route eigrp 172.16.0.0
! Should have no 172.16.x.x routes (not yet configured)
```

---

## 5. Lab Challenge: Core Implementation

> Complete each objective in order. Verify each before moving to the next.

### Objective 1 — Add Loopback Interfaces on R2

Configure two additional loopback interfaces on R2 to simulate multiple server subnets:

1. **Loopback1:** 172.16.20.1/24 (network 172.16.20.0/24)
2. **Loopback2:** 172.16.21.1/24 (network 172.16.21.0/24)

Add these interfaces to EIGRP using the network command so they are advertised:
```
network 172.16.20.0 0.0.0.255
network 172.16.21.0 0.0.0.255
```

Verify R1 learns both 172.16.20.0/24 and 172.16.21.0/24 as individual routes:
```
R1# show ip route eigrp 172.16.0.0
```

### Objective 2 — Add Loopback Interfaces on R3

Configure two additional loopback interfaces on R3:

1. **Loopback1:** 172.16.30.1/24 (network 172.16.30.0/24)
2. **Loopback2:** 172.16.31.1/24 (network 172.16.31.0/24)

Add these to EIGRP:
```
network 172.16.30.0 0.0.0.255
network 172.16.31.0 0.0.0.255
```

Verify R1 learns both:
```
R1# show ip route eigrp 172.16.0.0
```

### Objective 3 — Configure Manual Summarization on R2

On R2, configure a summary route that aggregates Loopback1 and Loopback2 into a single /23 prefix.

The summary should be:
- **Summary prefix:** 172.16.20.0/23 (encompasses 172.16.20.0 and 172.16.21.0)
- **Outgoing interface:** Fa0/0 (toward R1)

Configure the summary:
```
router eigrp 100
 interface FastEthernet0/0
  ip summary-address eigrp 100 172.16.20.0 255.255.254.0
```

Verify on R2:
- Individual loopback routes still appear in the local routing table
- A null0 route for 172.16.20.0/23 is created

Verify on R1:
- Only the summary 172.16.20.0/23 appears (not the individual subnets)

### Objective 4 — Configure Manual Summarization on R3

On R3, configure a summary route for its loopbacks:

- **Summary prefix:** 172.16.30.0/23 (encompasses 172.16.30.0 and 172.16.31.0)
- **Outgoing interface:** Fa0/0 (toward R1)

Configure the summary:
```
router eigrp 100
 interface FastEthernet0/0
  ip summary-address eigrp 100 172.16.30.0 255.255.254.0
```

Verify on R3:
- Individual loopback routes still in local table
- Null0 route for 172.16.30.0/23 is created

Verify on R1:
- Only the summary 172.16.30.0/23 appears

### Objective 5 — Understand and Observe Null0 Routes

On both R2 and R3, examine the null0 discard route created by summarization:

```
R2# show ip route 172.16.20.0/23
! Output should show: "Routing entry for 172.16.20.0/23, supernet"
! "Route metric is 28160, traffic share count is 1"
! "directly connected, via Null0"
```

Verify that this route:
- Is administrative distance 5 (internal EIGRP summary)
- Points to Null0 (discard interface)
- Has a metric equal to the best metric of any included subnet

### Objective 6 — Test End-to-End Reachability with Summarization

From R1, verify you can reach the summarized subnets:
```
R1# ping 172.16.20.1 source 10.0.0.1
R1# ping 172.16.21.1 source 10.0.0.1
R1# ping 172.16.30.1 source 10.0.0.1
R1# ping 172.16.31.1 source 10.0.0.1
```

All pings should succeed. Verify the routing table on R1:
```
R1# show ip route 172.16.0.0
! Should show only two routes:
! D 172.16.20.0/23 via 10.12.0.2 (R2)
! D 172.16.30.0/23 via 10.13.0.2 (R3)
```

---

## 6. Verification & Analysis

### After Objective 1–2: Individual Subnets Advertised

Before summarization, verify each loopback is learned individually:

```
R1# show ip route eigrp 172.16.0.0
```

Expected output:
```
      172.16.0.0/16 is variably subnetted, 4 subnets, 2 masks
D        172.16.20.0/24 [90/XXX] via 10.12.0.2, Fa0/0
D        172.16.21.0/24 [90/XXX] via 10.12.0.2, Fa0/0
D        172.16.30.0/24 [90/XXX] via 10.13.0.2, Fa0/0
D        172.16.31.0/24 [90/XXX] via 10.13.0.2, Fa0/0
```

### After Objective 3–4: Summarization Active

After configuring summarization on R2 and R3:

```
R1# show ip route eigrp 172.16.0.0
```

Expected output:
```
      172.16.0.0/16 is variably subnetted, 2 subnets, 2 masks
D        172.16.20.0/23 [90/XXX] via 10.12.0.2, Fa0/0
D        172.16.30.0/23 [90/XXX] via 10.13.0.2, Fa0/0
```

Notice the reduction: 4 routes → 2 routes.

### After Objective 5: Null0 Route Verification

On R2:

```
R2# show ip route 172.16.20.0
```

Output includes:
```
Routing entry for 172.16.20.0/23, supernet
  Known via "eigrp 100", distance 5, metric 28160, type internal
  Redistributed by eigrp 100
  Routing Descriptor Blocks:
    * directly connected, via Null0
      Route metric is 28160, traffic share count is 1
```

The Null0 next-hop indicates traffic destined for 172.16.20.0/23 that doesn't match a more specific prefix will be discarded locally (not forwarded back out any interface).

### After Objective 6: End-to-End Reachability

```
R1# ping 172.16.20.1 source 10.0.0.1
Reply from 172.16.20.1: bytes=32 time=XX ms TTL=254
```

All pings should succeed, confirming that summarization does not break reachability to the included subnets.

---

## 7. Verification Cheatsheet

| Command | Purpose |
|---|---|
| `show ip interface brief` | List all loopback interfaces |
| `show ip route eigrp 172.16.0.0` | View EIGRP-learned routes in a specific subnet |
| `show ip route <prefix>` | Detailed info on one route — including metric, next-hop, type |
| `show ip eigrp topology 172.16.20.0` | View topology table entry for a specific subnet |
| `show ip summary-address eigrp` | List configured summary addresses per interface |
| `ping <ip> source <source-ip>` | Test end-to-end reachability with source address |

---

## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these steps first!

### R2 Configuration: Loopback + Network + Summarization

<details>
<summary>Click to view R2 Configuration</summary>

```bash
! R2 — Add Loopback interfaces and summarization
interface Loopback1
 ip address 172.16.20.1 255.255.255.0
!
interface Loopback2
 ip address 172.16.21.1 255.255.255.0
!
router eigrp 100
 network 172.16.20.0 0.0.0.255
 network 172.16.21.0 0.0.0.255
!
interface FastEthernet0/0
 ip summary-address eigrp 100 172.16.20.0 255.255.254.0
```

</details>

### R3 Configuration: Loopback + Network + Summarization

<details>
<summary>Click to view R3 Configuration</summary>

```bash
! R3 — Add Loopback interfaces and summarization
interface Loopback1
 ip address 172.16.30.1 255.255.255.0
!
interface Loopback2
 ip address 172.16.31.1 255.255.255.0
!
router eigrp 100
 network 172.16.30.0 0.0.0.255
 network 172.16.31.0 0.0.0.255
!
interface FastEthernet0/0
 ip summary-address eigrp 100 172.16.30.0 255.255.254.0
```

</details>

### Verification Commands

<details>
<summary>Click to view Key Verification Commands</summary>

```bash
! On R1 — Verify summarized routes
show ip route eigrp 172.16.0.0

! On R2 — Verify null0 route and loopbacks
show ip route 172.16.20.0
show ip interface brief | include Loopback

! On R3 — Verify null0 route and loopbacks
show ip route 172.16.30.0
show ip interface brief | include Loopback

! Test end-to-end reachability
R1# ping 172.16.20.1 source 10.0.0.1
R1# ping 172.16.21.1 source 10.0.0.1
```

</details>

---

## 9. Troubleshooting Scenarios

Each ticket simulates a real-world fault related to route summarization. Inject the fault first, then diagnose using only show commands.

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

### Ticket 1 — Summarization Creates a Black Hole

R1 can ping 172.16.20.1 (Loopback1 on R2) but cannot ping 172.16.21.1 (Loopback2 on R2). When you test from R2, both loopbacks reply. The network team suspects the summarization is causing a black hole for 172.16.21.x traffic.

**Inject:** `python3 scripts/fault-injection/inject_scenario_01.py`

**Symptoms:**
- `R1# ping 172.16.20.1` — succeeds
- `R1# ping 172.16.21.1` — fails (timeout)
- R2 receives the ping request (ICMP echo) but does not respond
- `show ip route 172.16.0.0` on R1 shows only 172.16.20.0/23 (summary exists)
- `show ip route 172.16.0.0` on R2 shows individual routes (Lo1, Lo2) but the summary is also present

**Success criteria:**
- Both 172.16.20.1 and 172.16.21.1 are reachable from R1
- Summarization remains active (172.16.20.0/23 in R1's table, not individual /24s)

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Check R1's routing table
R1# show ip route 172.16.20.0
! Should show summary 172.16.20.0/23

! From R1, test each loopback on R2
R1# ping 172.16.20.1 source 10.0.0.1
! Succeeds

R1# ping 172.16.21.1 source 10.0.0.1
! Fails

! The issue is that the summary route matches both, but only one subnet is actually advertised
! This suggests R2 has the 172.16.20.0/23 summary configured, but only Loopback1 exists
! (Loopback2 was not created)

! Check R2's loopback configuration
R2# show ip interface brief | include Loopback
! Loopback2 is MISSING

! The summary claims to cover 172.16.20.0 and 172.16.21.0, but .21.0 doesn't exist
! Any traffic to 172.16.21.x matches the summary and is sent to R2, where it is discarded by null0
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R2 — Add the missing Loopback2
R2(config)# interface Loopback2
R2(config-if)# ip address 172.16.21.1 255.255.255.0
R2(config-if)# exit

! Ensure the network statement for Lo2 is in EIGRP
R2(config)# router eigrp 100
R2(config-router)# network 172.16.21.0 0.0.0.255

! Verify the loopback and its route
R2# show ip interface brief | include Loopback
R2# show ip route 172.16.21.0

! Verify R1 can now reach both
R1# ping 172.16.21.1 source 10.0.0.1
! Should succeed
```

</details>

---

### Ticket 2 — Auto-Summary Causing Discontiguous Network Issues

After a configuration change, R1 can no longer reach R3's loopback subnets (172.16.30.x), even though R2 can still reach them. The network team suspects auto-summary is being re-enabled.

**Inject:** `python3 scripts/fault-injection/inject_scenario_02.py`

**Symptoms:**
- `R1# ping 172.16.30.1` — fails (timeout)
- `R3# ping 172.16.30.1 source 10.0.0.3` — succeeds (local)
- `show ip route eigrp 172.16.0.0` on R1 shows nothing or only shows 172.16.30.0/16 (too broad)
- `show run | section eigrp` on R3 may show auto-summary is enabled

**Success criteria:**
- Auto-summary is disabled on R3
- R1 learns 172.16.30.0/23 summary from R3
- R1 can ping 172.16.30.1 and 172.16.31.1

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Check if auto-summary is enabled on R3
R3# show run | section eigrp
! Look for: auto-summary (should see "no auto-summary", but might not)

! If auto-summary is enabled, R3 summarizes to classful boundary
! 172.16.x.x routes summarize to 172.16.0.0/16 by default
! This creates a routing black hole for routes outside the expected range

! Check what R1 sees
R1# show ip route eigrp 172.16.0.0
! If auto-summary is active, may see overly broad prefix or nothing

! Verify R3's neighbors on other routers
R1# show ip eigrp neighbors
R2# show ip eigrp neighbors
! R3 may still be advertising, but the route is incorrect
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R3 — Ensure no auto-summary is configured
R3(config)# router eigrp 100
R3(config-router)# no auto-summary

! Verify the manual summary is still in place
R3# show ip summary-address eigrp
! Should show: 172.16.30.0 255.255.254.0 on Fa0/0

! Verify R1 now learns the correct summary
R1# show ip route eigrp 172.16.30.0
! Should show 172.16.30.0/23 (not 172.16.0.0/16)

! Test reachability
R1# ping 172.16.30.1 source 10.0.0.1
! Should succeed
```

</details>

---

### Ticket 3 — Summary Route Not Appearing in Neighbor's Table

R1 should be learning a summary route 172.16.20.0/23 from R2, but it does not appear in R1's routing table. R2's loopbacks exist and are reachable. When you run `show ip summary-address eigrp` on R2, nothing is displayed.

**Inject:** `python3 scripts/fault-injection/inject_scenario_03.py`

**Symptoms:**
- `show ip route eigrp 172.16.0.0` on R1 shows individual routes (172.16.20.0/24, 172.16.21.0/24) instead of summary
- `show ip summary-address eigrp` on R2 shows nothing
- Configuration review shows the summary command is missing or on the wrong interface

**Success criteria:**
- Summary is configured on R2 Fa0/0
- R1 receives only the summary (not individual /24s)
- Null0 route exists on R2

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Check if summary is configured on R2
R2# show ip summary-address eigrp
! Output is empty — summary is not configured

! Verify the summary should be on Fa0/0 (toward R1)
R2# show ip interface Fa0/0 | include address
! Fa0/0 is 10.12.0.2/30 — correct interface to R1

! Check running config for summary command
R2# show run | section eigrp
! Summarization command may be missing entirely

! Check R1's view of the routes
R1# show ip route 172.16.0.0
! Shows individual /24 routes (172.16.20.0, 172.16.21.0)
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R2 — Add the summary configuration on Fa0/0
R2(config)# interface FastEthernet0/0
R2(config-if)# ip summary-address eigrp 100 172.16.20.0 255.255.254.0
R2(config-if)# exit

! Verify the summary now appears
R2# show ip summary-address eigrp
! Should show: "172.16.20.0 255.255.254.0 on Fa0/0"

! Verify the null0 route is created
R2# show ip route 172.16.20.0/23
! Should show next-hop "via Null0"

! Verify R1 now receives the summary (not individual routes)
R1# show ip route eigrp 172.16.20.0
! Should show: 172.16.20.0/23 [90/XXX] via 10.12.0.2
! (not individual .20 and .21)
```

</details>

---

### Ticket 4 — Null0 Route Missing or Incorrect

You notice that R2's routing table does not show a Null0 route for the summary prefix 172.16.20.0/23. The summary is configured and R1 receives it, but the discard route is absent. This could cause routing loops if subnets within the summary range are learned from elsewhere.

**Inject:** `python3 scripts/fault-injection/inject_scenario_04.py`

**Symptoms:**
- `show ip route 172.16.20.0/23` on R2 shows a regular next-hop (not Null0)
- Summary is configured on Fa0/0
- R1 correctly receives the summary
- EIGRP may be missing from the route source (shows as "static" or other)

**Success criteria:**
- Null0 route is created for 172.16.20.0/23
- Route source is EIGRP internal (AD 5)
- Null0 next-hop is confirmed

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Check the route for the summary
R2# show ip route 172.16.20.0
! May show next-hop as an interface (not Null0) or missing entirely

! Verify summary is configured
R2# show ip summary-address eigrp
! Should show the summary

! The null0 route should be automatically created when the summary is configured
! If it's missing, the summary command may have been applied incorrectly
! Or the interface may not be in EIGRP

! Check if Fa0/0 is EIGRP-enabled
R2# show ip eigrp interfaces
! Fa0/0 should appear

! Check if Fa0/0 is passive (passive interfaces don't send summaries)
R2# show run | section eigrp
! Look for: passive-interface Fa0/0 (should NOT be present)
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! Ensure the summary is on an active (non-passive) interface
R2(config)# interface FastEthernet0/0
R2(config-if)# no passive-interface
! (this is interface-level command, may not apply; use router-level instead)

! Verify at router level
R2(config)# router eigrp 100
R2(config-router)# no passive-interface FastEthernet0/0

! Reconfigure the summary if needed
R2(config-router)# exit
R2(config)# interface FastEthernet0/0
R2(config-if)# ip summary-address eigrp 100 172.16.20.0 255.255.254.0
R2(config-if)# exit

! Clear EIGRP neighbors to force re-sync
R2(config)# exit
R2# clear ip eigrp neighbors

! Verify the null0 route appears
R2# show ip route 172.16.20.0
! Should now show: "directly connected, via Null0"
```

</details>

---

### Ticket 5 — Inter-Summary Traffic Lost (Different Summary Ranges)

R1 can reach R2's summarized subnets (172.16.20.0/23) but cannot reach R3's (172.16.30.0/23). Both summaries are configured and both routers are neighbors with R1. Traffic from R2 to R3 works fine.

**Inject:** `python3 scripts/fault-injection/inject_scenario_05.py`

**Symptoms:**
- `R1# ping 172.16.20.1` — succeeds
- `R1# ping 172.16.30.1` — fails (timeout)
- `show ip route eigrp 172.16.0.0` on R1 shows both summaries (172.16.20.0/23 and 172.16.30.0/23)
- From R1 traceroute: 172.16.20.1 goes directly to R2, but 172.16.30.1 never reaches R3

**Success criteria:**
- Both summaries are reachable from R1
- No configuration is broken; the issue is routing or EIGRP metric related

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Check R1's routing table
R1# show ip route 172.16.0.0
! Both summaries should appear (R2 and R3)

! Trace the path
R1# trace 172.16.30.1
! Should show: R1 -> R3, but may show: R1 -> R2 -> R3 or timeout

! The issue may be:
! 1. R3 summary is configured on wrong interface (not Fa0/0 toward R1)
! 2. R3's loopbacks are not EIGRP-enabled (network statements missing)
! 3. R3 has no neighbor with R1 (Fa0/0 not up)

! Check R3's EIGRP configuration
R3# show ip eigrp interfaces
! Fa0/0 should appear (link to R1)

! Check R3's neighbors
R3# show ip eigrp neighbors
! R1 should appear as a neighbor

! Check if the summary is on the right interface
R3# show ip summary-address eigrp
! Should show summary on Fa0/0 (interface toward R1)
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! Verify R3's configuration
! Ensure loopbacks are configured with network statements
R3(config)# router eigrp 100
R3(config-router)# network 172.16.30.0 0.0.0.255
R3(config-router)# network 172.16.31.0 0.0.0.255

! Ensure summary is on Fa0/0 (toward R1)
R3(config-router)# exit
R3(config)# interface FastEthernet0/0
R3(config-if)# ip summary-address eigrp 100 172.16.30.0 255.255.254.0
R3(config-if)# exit

! Verify EIGRP adjacency with R1
R3(config)# exit
R3# show ip eigrp neighbors
! R1 should be listed

! Clear EIGRP if needed
R3# clear ip eigrp neighbors

! Test from R1
R1# ping 172.16.30.1 source 10.0.0.1
! Should succeed
```

</details>

---

## 10. Lab Completion Checklist

**Concepts**
- [ ] Understand manual summarization and how it reduces routing table size
- [ ] Explain the purpose of the null0 discard route created by summarization
- [ ] Understand the difference between manual summarization and auto-summary
- [ ] Identify summarization black holes and how to prevent them

**Configuration**
- [ ] Add Loopback1 and Loopback2 on R2 with correct IP addresses
- [ ] Add Loopback1 and Loopback2 on R3 with correct IP addresses
- [ ] Configure network statements in EIGRP to advertise loopback subnets
- [ ] Configure manual summary on R2 Fa0/0: 172.16.20.0/23
- [ ] Configure manual summary on R3 Fa0/0: 172.16.30.0/23
- [ ] Verify null0 routes exist on R2 and R3

**Verification**
- [ ] R1 learns 172.16.20.0/23 (not individual .20 and .21)
- [ ] R1 learns 172.16.30.0/23 (not individual .30 and .31)
- [ ] Routing table on R1 shows 2 summarized routes (down from 4 individual routes)
- [ ] Pings from R1 to all four loopbacks succeed: 172.16.20.1, 172.16.21.1, 172.16.30.1, 172.16.31.1
- [ ] Null0 routes visible on R2 and R3: `show ip route 172.16.20.0` and `show ip route 172.16.30.0`

**Troubleshooting**
- [ ] Ticket 1 diagnosed and resolved (black hole — missing loopback)
- [ ] Ticket 2 diagnosed and resolved (auto-summary re-enabled)
- [ ] Ticket 3 diagnosed and resolved (summary not advertised)
- [ ] Ticket 4 diagnosed and resolved (null0 route missing)
- [ ] Ticket 5 diagnosed and resolved (inter-summary reachability)

**End-to-End Verification**
- [ ] All neighbors established and stable
- [ ] All routes in topology table are Passive (P)
- [ ] Routing table on R1 shows only 2 prefixes in 172.16.0.0/16
- [ ] Pings from R1 to all destinations succeed
