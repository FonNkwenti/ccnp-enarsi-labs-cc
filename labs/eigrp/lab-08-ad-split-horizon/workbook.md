# EIGRP Lab 08 — Administrative Distance & Split Horizon: Advanced Path Control

**Exam:** CCNP ENARSI 300-410
**Difficulty:** Advanced
**Estimated Time:** 75 minutes

---

## 1. Concepts & Skills Covered

### Blueprint Coverage

| Blueprint ID | Topic |
|---|---|
| 1.1 | Troubleshoot administrative distance |
| 1.3 | Troubleshoot loop prevention mechanisms (split horizon, route poisoning) |

### Key Concepts

**Administrative Distance (AD)**

AD is a preference value (0–255) that determines which routing protocol takes precedence when multiple routes to the same destination exist:
- **AD 0:** Directly connected
- **AD 1:** Static route
- **AD 90:** EIGRP internal
- **AD 170:** EIGRP external
- **AD 110:** OSPF
- **AD 120:** RIP

A route with lower AD is preferred. For example, a static route (AD 1) overrides an EIGRP route (AD 90) to the same destination.

**Modifying EIGRP AD**

```
router eigrp AS
 distance eigrp <internal> <external>
```

Example:
```
distance eigrp 80 170   ! Internal: 80 (lower = more preferred), External: 170 (default)
```

**Split Horizon**

Split horizon prevents routing loops by suppressing route advertisements back out the interface they were learned on. In a hub-spoke topology, this can cause incomplete routing:

```
Hub (R1) ——— Branch A (R2)
    |
Branch B (R3)
```

If split horizon is enabled on R1's Fa0/0 (link to R2):
- R1 learns R3's loopback via Fa1/0 from R3
- R1 suppresses this route from being advertised back out Fa0/0 (learned on Fa1/0)
- R2 cannot reach R3's loopback via the hub's Fa0/0 (even though R1 has the route)

**Disabling Split Horizon**

```
router eigrp AS
 interface FastEthernet X/Y
  no ip split-horizon eigrp AS
```

This re-enables the route to be advertised back out Fa0/0, allowing R2 to learn R3's loopback via R1.

---

## 2. Topology & Scenario

### Enterprise Scenario

Acme Corp has deployed a hub-spoke topology with R1 as the hub. A floating static route exists on R1 pointing toward R3 as a backup to the EIGRP route to R2. You will modify EIGRP's internal AD to influence route selection, and you will disable split horizon on R1 to allow hub-spoke reachability. These techniques demonstrate advanced path control and are critical for exam mastery.

This lab continues from Lab 07 — R1, R2, R3, and R4 are fully configured with EIGRP, filtering, and proper adjacencies. You will now manipulate AD and split horizon to demonstrate their impact on routing decisions.

### Topology Reference

The four-router network from Lab 07 continues, with focus on the hub-spoke relationship:
- **R1** (Hub): Will have EIGRP AD modified and split horizon disabled on Fa0/0
- **R2** (Branch A): Relies on R1 to reach R3
- **R3** (Branch B): Will have a static route as backup
- **R4** (Stub): Unchanged

---

## 3. Hardware & Environment Specifications

### Device Platform Summary

| Device | Platform | Role | RAM | IOS Image |
|---|---|---|---|---|
| R1 | c7200 | Hub / Core | 512 MB | c7200-adventerprisek9-mz.153-3.XB12.image |
| R2 | c3725 | Branch A | 256 MB | c3725-adventerprisek9-mz.124-15.T14.image |
| R3 | c3725 | Branch B | 256 MB | c3725-adventerprisek9-mz.124-15.T14.image |
| R4 | c3725 | Stub/Edge | 256 MB | c3725-adventerprisek9-mz.124-15.T14.image |

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

The initial configuration for Lab 08 is the **exact working solution from Lab 07** — R1, R2, R3, and R4 are fully configured with EIGRP, filtering, and proper adjacencies. No static routes, AD modifications, or split horizon changes exist yet.

**Pre-configured (from Lab 07):**
- ✅ EIGRP AS 100 on all four routers
- ✅ All adjacencies and proper routing
- ✅ Filtering on R3 (blocks 192.168.4.0/24)

**Not pre-configured (your task):**
- ❌ Static routes for AD manipulation
- ❌ EIGRP AD modification (distance eigrp)
- ❌ Split horizon disabling

Verify the base state:
```
R1# show ip route eigrp 10.0.0.3
! Should show via R3 directly (Fa1/0) and via R2 (Fa0/0) with equal cost

R1# show ip split-horizon eigrp 100 Fa0/0
! Should show: eigrp 100 split horizon is enabled (default)
```

---

## 5. Lab Challenge: Core Implementation

> Complete each objective in order. Verify each before moving to the next.

### Objective 1 — Examine Current Route Preferences and AD Values

Inspect R1's routing table and verify the current AD values for EIGRP routes:

```
R1# show ip route 10.0.0.2
! Should show [90/XXX] — AD 90 (EIGRP internal default)

R1# show ip route eigrp
! All routes should show AD 90 (internal) or 170 (external)
```

Also check the distribution of the route to 10.0.0.3 if there are multiple paths:

```
R1# show ip eigrp topology 10.0.0.3
! Note: there may be equal-cost paths via R2 and R3, or only via R3
```

### Objective 2 — Create a Floating Static Route on R1

Add a static route on R1 as a backup to EIGRP for destination 10.0.0.3/32:

```
ip route 10.0.0.3 255.255.255.255 10.12.0.2 91
```

This static route:
- Points to 10.0.0.3 via R2 (10.12.0.2)
- Has AD 91 (higher than EIGRP's default 90, so EIGRP is preferred)
- Only becomes active if EIGRP route is lost

Verify the route is not in the active routing table:

```
R1# show ip route 10.0.0.3
! Should show EIGRP route [90/XXX], not the static route [91/1]
```

### Objective 3 — Modify EIGRP Internal AD on R1 to Reduce Preference

Change the EIGRP internal AD from 90 to 80, making EIGRP even more preferred:

```
router eigrp 100
 distance eigrp 80 170
```

This change:
- Reduces internal AD from 90 to 80 (lower is better)
- Does not affect external routes (AD 170)
- Makes EIGRP more attractive than the floating static route

Verify R1 still prefers the EIGRP route:

```
R1# show ip route 10.0.0.3
! Should show [80/XXX] (EIGRP, with new AD)
! Static route remains inactive
```

### Objective 4 — Observe Split Horizon Suppression on R1 Fa0/0

Examine what routes R1 advertises out Fa0/0 (link to R2). Due to split horizon, R1 should NOT advertise routes learned on Fa0/0 back out Fa0/0. Test this by checking what R2 receives:

```
R1# show ip split-horizon eigrp 100 Fa0/0
! Should show: eigrp 100 split horizon is enabled

R2# show ip route 10.0.0.3
! Is this route learned via R1 (Fa0/0) or via R3 (Fa0/1)?
! Due to split horizon, R2 learns R3 via R3 directly (Fa0/1), not via R1 (Fa0/0)
```

Document this behavior before disabling split horizon.

### Objective 5 — Disable Split Horizon on R1 Fa0/0

Disable split horizon on R1's Fa0/0 interface:

```
router eigrp 100
 interface FastEthernet0/0
  no ip split-horizon eigrp 100
```

This allows R1 to advertise R3's routes back out Fa0/0 to R2, even though the route was learned on Fa1/0.

### Objective 6 — Verify R2 Now Learns R3 Routes via R1

After disabling split horizon, check R2's routing table:

```
R2# show ip route 10.0.0.3
! Now should show next-hop 10.12.0.1 (R1's Fa0/0) instead of 10.23.0.2 (R3's Fa0/1)
! Note: R2 may have equal-cost load balancing for 10.0.0.3
```

The key difference: previously, R2 learned R3's loopback directly from R3. Now, R2 can learn it via R1 as well.

### Objective 7 — Verify the Impact: Reduce Core Router Queries

Without split horizon disabled, during a reconvergence event, R3 would be consulted as a neighbor. With split horizon disabled on the hub and routes advertised back to R2, R2 can provide alternative paths, reducing the query burden on R3.

Test this conceptually by examining the neighbor topology:

```
R1# show ip eigrp neighbors
! Note all neighbors

R1# show ip eigrp topology 10.0.0.3
! Verify the route shows both R2 and R3 as sources (if variance allows)
```

---

## 6. Verification & Analysis

### After Objective 1: Current Route Preferences

```
R1# show ip route 10.0.0.3
```

Expected output:
```
D        10.0.0.3/32 [90/158720] via 10.13.0.2, Fa1/0
```

AD is 90 (default EIGRP internal).

### After Objective 2–3: Static Route and AD Modification

```
R1# show ip route 10.0.0.3
```

Expected output after AD change:
```
D        10.0.0.3/32 [80/158720] via 10.13.0.2, Fa1/0
```

AD changed to 80. The static route remains inactive (not shown because EIGRP is preferred).

### After Objective 4: Split Horizon Behavior (Before Disabling)

```
R2# show ip route 10.0.0.3
```

Expected output (before disabling split horizon):
```
D        10.0.0.3/32 [90/158720] via 10.23.0.2, Fa0/1
```

R2 learns R3 directly (via Fa0/1, link to R3), not via R1 (due to split horizon).

### After Objective 5–6: Split Horizon Disabled

```
R2# show ip route 10.0.0.3
```

Expected output (after disabling split horizon on R1 Fa0/0):
```
D        10.0.0.3/32 [90/158720] via 10.12.0.1, Fa0/0
                      [90/158720] via 10.23.0.2, Fa0/1
```

R2 now has equal-cost load balancing: it can reach R3 directly (via Fa0/1) AND via R1 (via Fa0/0).

---

## 7. Verification Cheatsheet

| Command | Purpose |
|---|---|
| `show ip route <prefix>` | Verify route is in table and check AD value |
| `show ip split-horizon eigrp AS interface` | Verify split horizon status per interface |
| `show run \| section eigrp` | View EIGRP config including distance and interface commands |
| `show run \| begin interface FastEthernet` | View interface-specific configs |
| `show ip eigrp topology <prefix>` | View topology for a specific route |
| `show ip eigrp neighbors` | Verify all neighbors are present |

---

## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these steps first!

### R1 Configuration: Static Route, AD, and Split Horizon

<details>
<summary>Click to view R1 Configuration</summary>

```bash
! R1 — Add floating static route for 10.0.0.3
ip route 10.0.0.3 255.255.255.255 10.12.0.2 91

! R1 — Modify EIGRP internal AD
router eigrp 100
 distance eigrp 80 170

! R1 — Disable split horizon on Fa0/0
router eigrp 100
 interface FastEthernet0/0
  no ip split-horizon eigrp 100
```

</details>

### Verification Commands

<details>
<summary>Click to view Key Verification Commands</summary>

```bash
! Verify AD modification
show ip route 10.0.0.3

! Verify split horizon status
show ip split-horizon eigrp 100 FastEthernet0/0

! Verify configuration
show run | section eigrp
show run | section "ip route"

! Verify R2 now has dual paths via R1 and R3
R2# show ip route 10.0.0.3
```

</details>

---

## 9. Troubleshooting Scenarios

Each ticket simulates a real-world fault related to AD and split horizon. Inject the fault first, then diagnose.

### Workflow

```bash
python3 setup_lab.py
python3 scripts/fault-injection/inject_scenario_01.py
# Troubleshoot and fix
python3 scripts/fault-injection/apply_solution.py
```

---

### Ticket 1 — Split Horizon Causing Incomplete Routing in Hub-Spoke

In a hub-spoke topology (R1 hub, R2 and R3 as branches), R2 cannot reach R3 because split horizon is preventing R1 from advertising R3's routes. R3 can reach R2 via the direct link or via R1, but R2 only knows about R3 via the direct link, creating asymmetric routing.

**Inject:** `python3 scripts/fault-injection/inject_scenario_01.py`

**Symptoms:**
- R2 can reach R3, but only via the direct link (Fa0/1)
- R2 does not learn R3's routes via R1 (Fa0/0)
- Split horizon is enabled on R1 Fa0/0 (default)
- During R2-R3 link failure, R2 cannot reach R3

**Success criteria:**
- R2 learns R3 routes via both direct link and via R1
- Split horizon is disabled on R1 Fa0/0
- Dual paths available for convergence redundancy

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Check R2's routing to R3
R2# show ip route 10.0.0.3
! Currently shows only via 10.23.0.2 (direct link), not via 10.12.0.1 (R1)

! Check R1's split horizon setting on Fa0/0
R1# show ip split-horizon eigrp 100 Fa0/0
! Should show "split horizon is enabled"

! Check if split horizon is blocking routes
R1# show run | section eigrp
! Look for: "no ip split-horizon" (should NOT be present)
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R1 — Disable split horizon on Fa0/0
R1(config)# router eigrp 100
R1(config-router)# interface FastEthernet0/0
R1(config-if)# no ip split-horizon eigrp 100
R1(config-if)# exit

! Verify split horizon is disabled
R1# show ip split-horizon eigrp 100 Fa0/0
! Should show "split horizon is disabled"

! Verify R2 now learns R3 via R1
R2# show ip route 10.0.0.3
! Should now show dual next-hops: via R1 (10.12.0.1) and via R3 (10.23.0.2)
```

</details>

---

### Ticket 2 — AD Not Influencing Route Preference

A floating static route was configured with AD 95, intended to be less preferred than EIGRP (AD 90). However, the static route is being used instead of EIGRP, suggesting the AD values are reversed or EIGRP route is missing.

**Inject:** `python3 scripts/fault-injection/inject_scenario_02.py`

**Symptoms:**
- `show ip route 10.0.0.3` shows [95/1] (static) instead of [90/XXX] (EIGRP)
- EIGRP route exists in the topology but not in the routing table
- Static route is active even though it should be passive

**Success criteria:**
- EIGRP route is preferred (lower AD takes precedence)
- Static route is inactive (shown in running config but not in active routing table)
- Convergence time uses EIGRP, not static route

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Check the routing table
R1# show ip route 10.0.0.3
! If static is active, EIGRP is either missing or has higher AD

! Check topology to see if EIGRP route exists
R1# show ip eigrp topology 10.0.0.3
! Should show EIGRP has a route

! Check the static route configuration
R1# show run | include "ip route"
! Verify AD value is correct (should be > 90 for floating static)

! Check EIGRP AD
R1# show run | section eigrp
! Look for: "distance eigrp <internal> <external>"
! If internal is > 90 or missing, that's the problem
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! Verify EIGRP has the route and ensure AD is less than static
R1(config)# router eigrp 100
R1(config-router)# distance eigrp 90 170  ! Or lower (e.g., 80)

! Verify the static route AD is higher
R1(config)# show run | include "ip route"
! Should show: ip route 10.0.0.3 255.255.255.255 10.12.0.2 95
! (or any value > 90)

! Verify EIGRP route is now preferred
R1# show ip route 10.0.0.3
! Should show EIGRP [90/XXX] or [80/XXX] (whichever was set)
```

</details>

---

### Ticket 3 — Static Route Override Failing (AD Misconfigured)

An administrator configured a static route with AD 80, intending it to override EIGRP (AD 90). However, EIGRP is still being used, and the static route is never activated.

**Inject:** `python3 scripts/fault-injection/inject_scenario_03.py`

**Symptoms:**
- Static route is configured with AD 80 (lower than EIGRP)
- `show ip route 10.0.0.3` shows EIGRP [90/XXX], not static [80/1]
- Static route is not in the active routing table

**Success criteria:**
- Static route with lower AD overrides EIGRP
- Active route shows [80/1] via static path
- EIGRP becomes the backup when static fails

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Check the routing table
R1# show ip route 10.0.0.3
! Currently shows EIGRP (should be showing static if AD is lower)

! Check the static route config
R1# show run | include "ip route"
! Verify AD is < 90 (e.g., 80)

! Check EIGRP AD
R1# show run | section eigrp
! If "distance eigrp 80" is set, static AD must be < 80 to override

! Check if the static route is reachable
R1# show ip route 10.12.0.2
! Verify that 10.12.0.2 (next-hop of static route) is reachable
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! Determine the correct AD:
! If EIGRP internal AD is 90, static AD should be < 90 (e.g., 80)
! If EIGRP internal AD is 80, static AD should be < 80 (e.g., 75)

! Example fix (assuming EIGRP is 90):
R1(config)# ip route 10.0.0.3 255.255.255.255 10.12.0.2 80

! Verify the static route is now preferred
R1# show ip route 10.0.0.3
! Should show [80/1] via static

! If EIGRP must be preferred, increase static AD:
R1(config)# ip route 10.0.0.3 255.255.255.255 10.12.0.2 95
! (AD 95 > 90, so EIGRP is preferred)
```

</details>

---

### Ticket 4 — Split Horizon Not Disabled Properly

An administrator attempted to disable split horizon on R1 Fa0/0, but the command did not take effect. R2 still cannot reach R3 via R1 (split horizon is still active).

**Inject:** `python3 scripts/fault-injection/inject_scenario_04.py`

**Symptoms:**
- R2 cannot reach R3 via R1 (only via direct link)
- Command was entered but split horizon is still enabled
- Configuration may have been applied to wrong interface or wrong EIGRP AS

**Success criteria:**
- Split horizon is disabled on R1 Fa0/0
- R2 learns R3 routes via R1
- Configuration is correct

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Check split horizon status on R1 Fa0/0
R1# show ip split-horizon eigrp 100 Fa0/0
! If "enabled", the "no ip split-horizon" command didn't work

! Check the configuration
R1# show run interface FastEthernet0/0 | section eigrp
! Look for: "no ip split-horizon eigrp 100"
! If not present, command wasn't applied

! Verify the interface is correct (Fa0/0, not Fa0/1 or other)
R1# show ip interface brief | include Fa0
! Fa0/0 is the link to R2 (correct)
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! Enter router EIGRP configuration mode
R1(config)# router eigrp 100

! Enter interface configuration for Fa0/0
R1(config-router)# interface FastEthernet0/0

! Disable split horizon
R1(config-if)# no ip split-horizon eigrp 100

! Exit and verify
R1(config-if)# exit
R1(config-router)# exit
R1# show ip split-horizon eigrp 100 Fa0/0
! Should now show "split horizon is disabled"

! Verify R2's routing
R2# show ip route 10.0.0.3
! Should now show dual paths
```

</details>

---

### Ticket 5 — External AD Not Affecting Redistribution

An external EIGRP route (AD 170 by default) is being preferred over a static route (AD 1). The administrator tried to modify the external AD to prevent this, but it did not work.

**Inject:** `python3 scripts/fault-injection/inject_scenario_05.py`

**Symptoms:**
- External EIGRP route [170/XXX] is in the routing table (shouldn't be preferred over static)
- Static route is not being used as a backup
- External AD modification may not have been applied

**Success criteria:**
- Static route (AD 1) is preferred over external EIGRP (AD 170)
- External EIGRP becomes backup if static fails
- Configuration is correct

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! Check the routing table for external routes
R1# show ip route eigrp 172.0.0.0
! If showing external routes as primary, check their AD

! Check if static route exists
R1# show run | include "ip route"
! Verify a static route is configured with lower AD than 170

! Check EIGRP distance configuration
R1# show run | section eigrp
! Look for: "distance eigrp <internal> <external>"

! If external AD is still 170 (default), static route (AD 1) should be preferred
! The issue may be that no static route is configured, or the route doesn't exist
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! Verify static route exists with correct AD
R1(config)# ip route <destination> <mask> <next-hop> 1

! Or, if you want to increase external AD (less preferred):
R1(config)# router eigrp 100
R1(config-router)# distance eigrp 90 200  ! External AD = 200 (higher, less preferred)

! Verify static route is now preferred
R1# show ip route <destination>
! Should show static [1/0] as primary

! Verify EIGRP external routes are backup
R1# show ip route eigrp <destination>
! May show with "Redistributed" note if it's external
```

</details>

---

## 10. Lab Completion Checklist

**Concepts**
- [ ] Understand Administrative Distance (AD) and how it influences route preference
- [ ] Understand how lower AD is preferred over higher AD
- [ ] Explain split horizon and how it prevents routing loops in point-to-point topologies
- [ ] Understand when split horizon should be disabled (hub-spoke with multiple branches)
- [ ] Understand floating static routes and their purpose

**Configuration**
- [ ] Add floating static route on R1: 10.0.0.3/32 via R2 with AD 91
- [ ] Modify EIGRP internal AD on R1 to 80 (from default 90)
- [ ] Disable split horizon on R1 Fa0/0 (router and interface level)

**Verification**
- [ ] Static route is in running config but NOT active (EIGRP preferred)
- [ ] EIGRP route shows [80/XXX] (modified AD)
- [ ] R1 shows split horizon disabled on Fa0/0
- [ ] R2 learns R3 routes via R1 (Fa0/0) and via R3 (Fa0/1)
- [ ] R2 has equal-cost load balancing for R3 routes (after split horizon disabled)

**Troubleshooting**
- [ ] Ticket 1 diagnosed and resolved (split horizon blocking hub-spoke reachability)
- [ ] Ticket 2 diagnosed and resolved (AD not influencing preference)
- [ ] Ticket 3 diagnosed and resolved (static override not working)
- [ ] Ticket 4 diagnosed and resolved (split horizon not disabled properly)
- [ ] Ticket 5 diagnosed and resolved (external AD not affecting redistribution)

**End-to-End Verification**
- [ ] All neighbors stable
- [ ] R1 prefers EIGRP over floating static route
- [ ] R2 has redundant paths to R3 (via R1 and direct)
- [ ] Hub-spoke topology is fully meshed with dual paths
- [ ] EIGRP AD modification is active and visible in routing table
