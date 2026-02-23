# EIGRP Lab 07 — Route Filtering & Route Maps: Selective Advertisement

**Exam:** CCNP ENARSI 300-410
**Difficulty:** Advanced
**Estimated Time:** 90 minutes

---

## 1. Concepts & Skills Covered

### Blueprint Coverage

| Blueprint ID | Topic |
|---|---|
| 1.2 | Troubleshoot route map (filtering, tagging) |
| 1.3 | Troubleshoot loop prevention mechanisms (split horizon, route poisoning) |

### Key Concepts

**Distribute List with Prefix List**

A distribute-list filters which routes are advertised or received. It uses a prefix-list to specify which prefixes to allow or deny:

```
router eigrp AS
 distribute-list prefix-list INBOUND in interface <if>    ! Inbound: filter routes received
 distribute-list prefix-list OUTBOUND out interface <if>   ! Outbound: filter routes advertised
```

A prefix-list defines allowed/denied IP prefixes:

```
ip prefix-list BLOCK-R4 seq 5 deny 192.168.4.0/24         ! Block R4's loopback
ip prefix-list BLOCK-R4 seq 10 permit 0.0.0.0/0 le 32     ! Allow everything else
```

**Route Map for Tagging**

A route-map can set and match route properties (tags) for loop prevention and policy:

```
route-map TAG-R4 permit 10
 match prefix-list ALLOW-R4
 set tag 40
!
route-map TAG-R4 permit 20
 match tag 40
 set tag 50
```

Redistribution with tagging prevents leaked routes from being re-advertised:

```
redistribute eigrp 100 route-map TAG-R4
```

**Implicit Deny**

Both prefix-lists and route-maps have an implicit deny at the end. If a prefix does not match any explicit permit statement, it is denied:

```
ip prefix-list ALLOW-LO seq 10 permit 10.0.0.1/32      ! Only allow R1's loopback
! Implicit deny all others
```

**Direction: In vs. Out**

- **In (inbound):** Filters routes **received** from a neighbor (affects this router's routing table)
- **Out (outbound):** Filters routes **advertised to** a neighbor (affects what neighbors learn)

---

## 2. Topology & Scenario

### Enterprise Scenario

Acme Corp wants to isolate R4's stub network (192.168.4.0/24, Loopback1) so that only R1 can reach it directly; R2 and R3 should not learn about R4's loopback. By applying a distribute-list on R3's inbound interface from R1, you will filter out R4's loopback prefix, demonstrating route filtering and loop prevention.

This lab continues from Lab 06 — R1, R2, R3, and R4 are fully configured with EIGRP and stub routing. You will now add a loopback interface to R4 and configure filtering.

### Topology Reference

The four-router network from Lab 06 continues:
- **R1** (Hub): Learns and advertises all routes, including R4's loopback (192.168.4.0/24)
- **R2** (Branch A): Receives and advertises normally
- **R3** (Branch B): Will have filtering applied to block R4's loopback
- **R4** (Stub): Advertises loopback1 (192.168.4.0/24) via R1

```
    ┌────────────────────────┐
    │         R1 (Hub)       │
    │  Learns all, including │
    │    192.168.4.0/24      │
    └────────────────────────┘
           /    |    \
          /     |     \
    ┌────┐  ┌───┐  ┌────┐
    │ R2 │  │ R3│  │ R4 │
    │    │  │   │  │    │
    └────┘  └───┘  │    │ ← Loopback1:
                   │    │   192.168.4.0/24
                   └────┘

    R3 will BLOCK 192.168.4.0/24 inbound
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
| R4 | Loopback1 | 192.168.4.0/24 (Loopback1 IP: 192.168.4.1) |

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

The initial configuration for Lab 07 is the **exact working solution from Lab 06** — R1, R2, R3, and R4 are fully configured with EIGRP, stub routing on R4, and proper adjacencies. R4 has only Loopback0 (10.0.0.4/32) configured; Loopback1 (192.168.4.0/24) does not yet exist.

**Pre-configured (from Lab 06):**
- ✅ EIGRP AS 100 on all four routers
- ✅ R4 configured as stub (eigrp stub connected summary)
- ✅ All adjacencies established
- ✅ Full IPv4 reachability

**Not pre-configured (your task):**
- ❌ Loopback1 on R4 (192.168.4.0/24)
- ❌ Network statement for Loopback1 on R4
- ❌ Prefix-list definitions
- ❌ Route-map definitions
- ❌ Distribute-list configuration

Verify the base state:
```
R4# show ip interface brief | include Loopback
! Should show only Loopback0

R1# show ip route eigrp 192.168.0.0
! Should have no 192.168.x.x routes (not yet configured)
```

---

## 5. Lab Challenge: Core Implementation

> Complete each objective in order. Verify each before moving to the next.

### Objective 1 — Add Loopback1 to R4 and Advertise via EIGRP

On R4, configure Loopback1 with IP address 192.168.4.1/24:

```
interface Loopback1
 ip address 192.168.4.1 255.255.255.0
!
router eigrp 100
 network 192.168.4.0 0.0.0.255
```

Verify R1 learns 192.168.4.0/24:
```
R1# show ip route 192.168.4.0
! Should show [90/XXX] via 10.14.0.2, Fa1/1

R1# ping 192.168.4.1 source 10.0.0.1
! Should succeed
```

Also verify R2 and R3 learn it (they should, via R1):
```
R2# show ip route 192.168.4.0
R3# show ip route 192.168.4.0
```

### Objective 2 — Create a Prefix-List on R3 to Block 192.168.4.0/24

On R3, create a prefix-list that denies the R4 loopback:

```
ip prefix-list BLOCK-R4-LO seq 5 deny 192.168.4.0/24
ip prefix-list BLOCK-R4-LO seq 10 permit 0.0.0.0/0 le 32
```

This prefix-list:
- **Denies** 192.168.4.0/24 (R4's loopback)
- **Permits** everything else (0.0.0.0/0 with any prefix length up to 32)

### Objective 3 — Apply Distribute-List Inbound on R3 Fa0/0 (Link to R1)

On R3, apply the prefix-list to filter inbound routes from R1:

```
router eigrp 100
 distribute-list prefix-list BLOCK-R4-LO in FastEthernet0/0
```

This tells R3: "When you receive routes from R1 via Fa0/0, block 192.168.4.0/24."

### Objective 4 — Verify R3 No Longer Has 192.168.4.0/24 in Its Routing Table

After applying the distribute-list:

```
R3# show ip route 192.168.4.0
! Should return "% Network not in table" or no route found

R3# ping 192.168.4.1 source 10.0.0.3
! Should fail (timeout) — R3 has no route to 192.168.4.0
```

### Objective 5 — Verify R1 and R2 Still Have 192.168.4.0/24

Confirm that filtering only applies to R3:

```
R1# show ip route 192.168.4.0
! Should show [90/XXX] via 10.14.0.2, Fa1/1

R1# ping 192.168.4.1 source 10.0.0.1
! Should succeed

R2# show ip route 192.168.4.0
! Should show [90/XXX] via 10.12.0.1, Fa0/0 (from R1)

R2# ping 192.168.4.1 source 10.0.0.2
! Should succeed
```

### Objective 6 — Verify R4 Still Advertises 192.168.4.0/24 (Stub Connected)

Confirm that R4 continues to advertise Loopback1 because it's a connected route and stub is configured as `connected summary`:

```
R4# show ip eigrp topology 192.168.4.0
! Should show: "P 192.168.4.0/24, 1 successors, FD is..."
! (Stub advertises connected routes)
```

### Objective 7 — (Optional) Create Route-Map for Tagging

For additional control, create a route-map on R1 that tags routes from R4:

```
route-map TAG-R4-ROUTES permit 10
 match tag 40
 set tag 50
!
route-map TAG-R4-ROUTES permit 20
! (implicit permit for non-matching)
```

This is an example of loop prevention via route tagging. A subsequent redistribute would use this map to avoid re-advertising tagged routes.

---

## 6. Verification & Analysis

### After Objective 1: R4 Loopback Learned by All Routers

Before filtering, verify all routers learn 192.168.4.0/24:

```
R1# show ip route 192.168.4.0
D        192.168.4.0/24 [90/XXX] via 10.14.0.2, Fa1/1

R2# show ip route 192.168.4.0
D        192.168.4.0/24 [90/XXX] via 10.12.0.1, Fa0/0

R3# show ip route 192.168.4.0
D        192.168.4.0/24 [90/XXX] via 10.13.0.1, Fa0/0
```

### After Objective 2–3: Prefix-List and Distribute-List Applied

After applying the distribute-list on R3 Fa0/0 inbound:

```
R3# show run | section eigrp
! Should include:
! distribute-list prefix-list BLOCK-R4-LO in FastEthernet0/0

R3# show run | section prefix-list
! Should show:
! ip prefix-list BLOCK-R4-LO seq 5 deny 192.168.4.0/24
! ip prefix-list BLOCK-R4-LO seq 10 permit 0.0.0.0/0 le 32
```

### After Objective 4: R3 No Route to 192.168.4.0/24

```
R3# show ip route 192.168.4.0
% Network not in table
```

Filtering is working correctly.

### After Objective 5: Other Routers Unaffected

```
R1# show ip route 192.168.4.0
D        192.168.4.0/24 [90/XXX] via 10.14.0.2, Fa1/1

R2# show ip route 192.168.4.0
D        192.168.4.0/24 [90/XXX] via 10.12.0.1, Fa0/0
```

R1 and R2 still have the route because the filtering is only on R3's Fa0/0 inbound, not on theirs.

---

## 7. Verification Cheatsheet

| Command | Purpose |
|---|---|
| `show ip prefix-list` | List all prefix-lists |
| `show ip prefix-list BLOCK-R4-LO` | View details of a specific prefix-list |
| `show route-map` | List all route-maps |
| `show run \| section prefix-list` | View prefix-list config |
| `show run \| section eigrp` | View EIGRP config including distribute-list |
| `show ip route <prefix>` | Check if a route exists in the table |
| `ping <ip> source <source-ip>` | Test reachability |

---

## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these steps first!

### R4 Configuration: Loopback1 and Network Statement

<details>
<summary>Click to view R4 Configuration</summary>

```bash
! R4 — Add Loopback1 and advertise via EIGRP
interface Loopback1
 ip address 192.168.4.1 255.255.255.0
!
router eigrp 100
 network 192.168.4.0 0.0.0.255
```

</details>

### R3 Configuration: Prefix-List and Distribute-List

<details>
<summary>Click to view R3 Configuration</summary>

```bash
! R3 — Create prefix-list to block R4's loopback
ip prefix-list BLOCK-R4-LO seq 5 deny 192.168.4.0/24
ip prefix-list BLOCK-R4-LO seq 10 permit 0.0.0.0/0 le 32

! R3 — Apply distribute-list on Fa0/0 inbound
router eigrp 100
 distribute-list prefix-list BLOCK-R4-LO in FastEthernet0/0
```

</details>

### Optional: R1 Route-Map for Tagging

<details>
<summary>Click to view R1 Route-Map (Optional)</summary>

```bash
! R1 — Create route-map for tagging (loop prevention)
route-map TAG-R4-ROUTES permit 10
 match prefix-list R4-LOOPBACK
 set tag 40
!
route-map TAG-R4-ROUTES permit 20
! (implicit permit for non-matching routes)

ip prefix-list R4-LOOPBACK seq 5 permit 192.168.4.0/24
```

</details>

### Verification Commands

<details>
<summary>Click to view Key Verification Commands</summary>

```bash
! Verify prefix-list is configured
show ip prefix-list BLOCK-R4-LO

! Verify distribute-list is applied
show run | section eigrp

! Verify R3 does NOT have 192.168.4.0/24
show ip route 192.168.4.0

! Verify R1 and R2 still have it
R1# show ip route 192.168.4.0
R2# show ip route 192.168.4.0

! Test reachability
R3# ping 192.168.4.1 source 10.0.0.3    ! Should fail
R1# ping 192.168.4.1 source 10.0.0.1    ! Should succeed
R2# ping 192.168.4.1 source 10.0.0.2    ! Should succeed
```

</details>

---

## 9. Troubleshooting Scenarios

Each ticket simulates a real-world fault related to route filtering and route maps. Inject the fault first, then diagnose using only show commands.

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

### Ticket 1 — Distribute-List Applied in Wrong Direction

The network team configured a distribute-list to block R4's loopback on R3, but it was applied outbound on Fa0/0 instead of inbound. As a result, R3 can still see 192.168.4.0/24, and other routers are also blocked from seeing R3's routes (unintended consequence).

**Inject:** `python3 scripts/fault-injection/inject_scenario_01.py`

**Symptoms:**
- R3 still has 192.168.4.0/24 in its routing table (filtering didn't work)
- R1 and R2 cannot reach R3's routes (blocked outbound)
- `show run | section eigrp` on R3 shows `distribute-list ... out FastEthernet0/0`

**Success criteria:**
- Distribute-list is applied inbound on R3 Fa0/0
- R3 no longer has 192.168.4.0/24
- R1 and R2 can still reach R3's routes

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! On R3 — Check distribute-list direction
R3# show run | section eigrp
! Look for: "distribute-list ... out" or "distribute-list ... in"

! If configured "out", it filters ADVERTISED routes (wrong direction)
! We want "in" to filter RECEIVED routes

! Check R3's routing table
R3# show ip route 192.168.4.0
! If 192.168.4.0/24 is present, the inbound filter is not working

! Check what R1 and R2 see
R1# show ip route 10.0.0.3
! If missing or via different path, the outbound filter is blocking it
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R3 — Remove wrong configuration and reapply correctly
R3(config)# router eigrp 100
R3(config-router)# no distribute-list prefix-list BLOCK-R4-LO out FastEthernet0/0

! Apply the correct inbound direction
R3(config-router)# distribute-list prefix-list BLOCK-R4-LO in FastEthernet0/0

! Verify
R3# show run | section eigrp
! Should show: "distribute-list prefix-list BLOCK-R4-LO in FastEthernet0/0"

! Check the routing table
R3# show ip route 192.168.4.0
! Should now be missing

! Verify R1 and R2 can reach R3
R1# show ip route 10.0.0.3
! Should show route to R3
```

</details>

---

### Ticket 2 — Implicit Deny Blocking All Routes

After configuring a distribute-list on R3, R3 can no longer reach ANY external routes — not just 192.168.4.0/24. The network team suspects the prefix-list has an implicit deny that is blocking everything.

**Inject:** `python3 scripts/fault-injection/inject_scenario_02.py`

**Symptoms:**
- R3 has no routes from R1 or R2 in its `show ip route eigrp`
- Only directly connected routes (10.13.0.0/30, Loopback0) are present
- Prefix-list is missing the "permit 0.0.0.0/0 le 32" statement

**Success criteria:**
- Prefix-list includes an explicit "permit all" statement
- R3 learns all routes except 192.168.4.0/24
- Full connectivity restored (except R3 → 192.168.4.x)

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! On R3 — Check the prefix-list configuration
R3# show ip prefix-list BLOCK-R4-LO
! Output should show:
!   seq 5 deny 192.168.4.0/24
!   seq 10 permit 0.0.0.0/0 le 32

! If seq 10 (permit all) is missing, that's the problem
! Prefix-lists have implicit deny at the end

! Check R3's routing table
R3# show ip route eigrp
! May show NO routes if implicit deny is blocking all
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R3 — Add the "permit all" statement to the prefix-list
R3(config)# ip prefix-list BLOCK-R4-LO seq 10 permit 0.0.0.0/0 le 32

! Verify the prefix-list
R3# show ip prefix-list BLOCK-R4-LO
! Should now show both seq 5 (deny) and seq 10 (permit)

! Routes should re-appear in the routing table
R3# show ip route eigrp
! Should now show routes from R1, R2, and R4 (except 192.168.4.0/24)

! Verify specific routes
R3# show ip route 192.168.4.0
! Should be missing (denied)

R3# show ip route 10.0.0.2
! Should be present (permitted)
```

</details>

---

### Ticket 3 — Prefix-List Sequence Error Blocking Wrong Route

A prefix-list was created to block 192.168.4.0/24, but due to a sequence numbering error, it's blocking 192.168.0.0/16 instead, affecting multiple subnets.

**Inject:** `python3 scripts/fault-injection/inject_scenario_03.py`

**Symptoms:**
- R3 cannot reach not only 192.168.4.0/24 but also other subnets in 192.168.0.0/16 (if they existed)
- Prefix-list line has incorrect subnet mask or prefix

**Success criteria:**
- Prefix-list blocks only 192.168.4.0/24
- All other routes are learned and reachable

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! On R3 — Check the prefix-list sequence
R3# show ip prefix-list BLOCK-R4-LO
! Look for the deny statement:
!   Should be: seq 5 deny 192.168.4.0/24
!   Wrong example: seq 5 deny 192.168.0.0/16  (too broad)

! Count how many routes are being blocked
R3# show ip route eigrp 192.168.0.0
! May show nothing if the entire 192.168.0.0/16 is denied
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R3 — Remove the incorrect sequence and reconfigure
R3(config)# no ip prefix-list BLOCK-R4-LO

! Reconfigure correctly
R3(config)# ip prefix-list BLOCK-R4-LO seq 5 deny 192.168.4.0/24
R3(config)# ip prefix-list BLOCK-R4-LO seq 10 permit 0.0.0.0/0 le 32

! Verify the prefix-list
R3# show ip prefix-list BLOCK-R4-LO
! Should show only the exact /24 being denied

! Verify the route now appears
R3# show ip route 192.168.4.0
! Should still be missing (correctly denied)
```

</details>

---

### Ticket 4 — Route-Map Tag Not Set or Matched Correctly

A route-map was created to tag R4 routes for loop prevention, but the tag is not being set or matched correctly. Routes are either missing tags or are not being affected by the route-map.

**Inject:** `python3 scripts/fault-injection/inject_scenario_04.py`

**Symptoms:**
- Route-map is configured but has logical errors (match before set, wrong sequence)
- Routes from R4 are not being tagged as expected
- Route-map sequences are out of order or missing

**Success criteria:**
- Route-map correctly matches and sets tags
- Tags can be verified with `show ip route <prefix> detail` (if supported) or `show route-map`

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! On R1 — Check the route-map configuration
R1# show route-map TAG-R4-ROUTES
! Look for:
!   permit seq 10 — match prefix-list (correct)
!   permit seq 20 — (permit all)

! Check for errors like:
!   Missing "set tag" command
!   Sequence out of order (match after set)

! Verify tags are being applied (if show commands support it)
R1# show ip route 192.168.4.0 detail
! May not show tag info in some IOS versions
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R1 — Remove incorrect route-map and reconfigure
R1(config)# no route-map TAG-R4-ROUTES

! Reconfigure correctly
R1(config)# route-map TAG-R4-ROUTES permit 10
R1(config-route-map)# match prefix-list R4-LOOPBACK
R1(config-route-map)# set tag 40
R1(config-route-map)# exit

R1(config)# route-map TAG-R4-ROUTES permit 20
! (implicit permit for non-matching)

! Verify the route-map
R1# show route-map TAG-R4-ROUTES
! Should show sequences in order with match and set commands

! Verify prefix-list exists
R1# show ip prefix-list R4-LOOPBACK
```

</details>

---

### Ticket 5 — Filtered Route Still Appearing in Routing Table

Despite configuring a distribute-list to block 192.168.4.0/24 on R3 Fa0/0 inbound, the route still appears in R3's routing table. This suggests the distribute-list is not being recognized or applied.

**Inject:** `python3 scripts/fault-injection/inject_scenario_05.py`

**Symptoms:**
- `show ip route 192.168.4.0` on R3 shows the route (should be missing)
- Distribute-list is configured: `distribute-list prefix-list BLOCK-R4-LO in Fa0/0`
- Prefix-list exists and appears correct

**Success criteria:**
- Distribute-list is removed and reapplied (forces refresh)
- Route is successfully filtered out
- No syntax errors in configuration

<details>
<summary>Click to view Diagnosis Steps</summary>

```bash
! On R3 — Verify distribute-list configuration
R3# show run | section eigrp
! Should show: distribute-list prefix-list BLOCK-R4-LO in FastEthernet0/0

! Verify prefix-list
R3# show ip prefix-list BLOCK-R4-LO
! Should show both deny and permit statements

! The issue may be that the distribute-list was configured BEFORE
! the prefix-list existed, so it was never applied

! Or EIGRP neighbors may need to be cleared to re-sync
```

</details>

<details>
<summary>Click to view Fix</summary>

```bash
! On R3 — Clear the distribute-list and reapply it
R3(config)# router eigrp 100
R3(config-router)# no distribute-list prefix-list BLOCK-R4-LO in FastEthernet0/0
R3(config-router)# distribute-list prefix-list BLOCK-R4-LO in FastEthernet0/0

! Alternatively, clear EIGRP neighbors to force re-sync
R3(config-router)# exit
R3# clear ip eigrp neighbors

! Verify the route is now filtered
R3# show ip route 192.168.4.0
! Should now be missing

! Verify other routes are still present
R3# show ip route eigrp 10.0.0.0
! Should show routes from R1 and R2
```

</details>

---

## 10. Lab Completion Checklist

**Concepts**
- [ ] Understand prefix-lists and how they define allowed/denied prefixes
- [ ] Understand distribute-lists and inbound vs. outbound directions
- [ ] Understand implicit deny in prefix-lists and route-maps
- [ ] Understand route-maps for tagging and loop prevention
- [ ] Understand the difference between "in" (receive) and "out" (advertise)

**Configuration**
- [ ] Add Loopback1 on R4 (192.168.4.0/24)
- [ ] Add network statement for Loopback1 on R4
- [ ] Create prefix-list on R3: BLOCK-R4-LO (deny 192.168.4.0/24, permit all)
- [ ] Apply distribute-list on R3 Fa0/0 inbound using the prefix-list
- [ ] (Optional) Create route-map on R1 for tagging

**Verification**
- [ ] All four routers learn 192.168.4.0/24 initially
- [ ] After filtering, R3 does NOT have 192.168.4.0/24
- [ ] R1 and R2 still have 192.168.4.0/24
- [ ] Pings from R3 to 192.168.4.1 fail (no route)
- [ ] Pings from R1 and R2 to 192.168.4.1 succeed
- [ ] Prefix-list shows both deny and permit statements
- [ ] Distribute-list configuration shows in running config

**Troubleshooting**
- [ ] Ticket 1 diagnosed and resolved (wrong direction)
- [ ] Ticket 2 diagnosed and resolved (implicit deny blocking all)
- [ ] Ticket 3 diagnosed and resolved (sequence error)
- [ ] Ticket 4 diagnosed and resolved (route-map tag issue)
- [ ] Ticket 5 diagnosed and resolved (filtered route still appearing)

**End-to-End Verification**
- [ ] All neighbors established and stable
- [ ] R1, R2 can reach R4's loopback; R3 cannot
- [ ] All other routes are still reachable
- [ ] Filtering is selective (only 192.168.4.0/24 is blocked on R3)
