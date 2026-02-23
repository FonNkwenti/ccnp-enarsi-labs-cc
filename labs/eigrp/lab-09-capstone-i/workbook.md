# EIGRP Lab 09 — Capstone I: Full Protocol Mastery

**Exam:** CCNP ENARSI 300-410
**Difficulty:** Advanced
**Estimated Time:** 120 minutes

---

## 1. Concepts & Skills Covered

### Blueprint Coverage

| Blueprint IDs | Topics |
|---|---|
| 1.9.a | EIGRP address families (IPv4, IPv6) |
| 1.9.b | Neighbor adjacency |
| 1.9.c | Loop-free path selection (RD, FD, FC, successor, feasible successor) |
| 1.9.d | EIGRP stub routing |
| 1.9.e | Load balancing (equal-cost, unequal-cost) |
| 1.9.f | Metrics (bandwidth, delay, K-values) |
| 1.1 | Administrative distance |
| 1.2 | Route map (filtering, tagging) |
| 1.3 | Loop prevention mechanisms (split horizon, route poisoning) |
| 1.5 | Summarization (manual and auto) |

### Key Concepts

This capstone lab integrates all EIGRP concepts from Labs 01–08. You are given only:
- A clean-slate topology (IP addressing only, no EIGRP)
- A set of configuration requirements (listed below in Section 5)
- No step-by-step guidance or configuration examples

Your task is to configure a complete EIGRP network from scratch, meeting all requirements, using the knowledge gained in previous labs.

---

## 2. Topology & Scenario

### Enterprise Scenario

Acme Corp is deploying a new EIGRP network across four locations. The requirements are:
- **R1 (Hub):** Central management router at corporate headquarters
- **R2 (Branch A):** Regional office with multiple server subnets
- **R3 (Branch B):** Second regional office with server subnets
- **R4 (Stub/Edge):** Remote branch that should not participate in transit routing

The network must:
1. Support full IPv4 and IPv6 connectivity
2. Implement proper metrics and path selection
3. Use stub routing on the edge router
4. Implement route summarization for scalability
5. Apply filtering and AD manipulation for policy control
6. Demonstrate loop prevention mechanisms

**Initial Condition:** Routers have only IP addressing and interface configuration; no EIGRP protocol is configured.

### Topology Reference

```
              ┌─────────────────────────┐
              │           R1            │
              │      (Hub / Core)       │
              │   IPv4: 10.0.0.1/32     │
              │   IPv6: 2001:db8::1/128 │
              └──────┬───────────┬──────┬───────────┐
           Fa0/0     │           │     Fa1/0      Fa1/1
     10.12.0.0/30    │           │   10.13.0.0/30 10.14.0.0/30
     2001:db8:12/64  │           │   2001:db8:13   2001:db8:14
                     │           │
     10.12.0.0/30    │           │   10.13.0.0/30
     2001:db8:12/64  │           │   2001:db8:13
           Fa0/0     │           │     Fa0/0
     ┌───────────────┘           └───────────────┐
     │                                           │
┌────┴──────────────┐           ┌────────────────┴────┐
│       R2          │           │       R3            │
│   (Branch A)      │           │   (Branch B)        │
│IPv4: 10.0.0.2/32 │           │ IPv4: 10.0.0.3/32   │
│IPv6: 2001:db8::2 │           │ IPv6: 2001:db8::3   │
└─────────┬─────────┘           └─────────┬───────────┘
      Fa0/1│                              │Fa0/1
10.23.0.0/30│                            │10.23.0.0/30
2001:db8:23  │                            │2001:db8:23
            └────────────────────────────┘

Plus Loopback networks on R2 (172.16.20/21) and R3 (172.16.30/31)
Plus Loopback1 on R4 (192.168.4.0/24)

┌──────────────┐
│     R4       │
│  (Stub)      │
│10.0.0.4/32   │
│192.168.4.0/24│
└──────────────┘
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

| Device | Interface | IPv4 Address | IPv6 Address |
|---|---|---|---|
| R1 | Loopback0 | 10.0.0.1/32 | 2001:db8::1/128 |
| R1 | FastEthernet0/0 | 10.12.0.1/30 | 2001:db8:12::1/64 |
| R1 | FastEthernet1/0 | 10.13.0.1/30 | 2001:db8:13::1/64 |
| R1 | FastEthernet1/1 | 10.14.0.1/30 | 2001:db8:14::1/64 |
| R2 | Loopback0 | 10.0.0.2/32 | 2001:db8::2/128 |
| R2 | Loopback1 | 172.16.20.1/24 | — |
| R2 | Loopback2 | 172.16.21.1/24 | — |
| R2 | FastEthernet0/0 | 10.12.0.2/30 | 2001:db8:12::2/64 |
| R2 | FastEthernet0/1 | 10.23.0.1/30 | 2001:db8:23::1/64 |
| R3 | Loopback0 | 10.0.0.3/32 | 2001:db8::3/128 |
| R3 | Loopback1 | 172.16.30.1/24 | — |
| R3 | Loopback2 | 172.16.31.1/24 | — |
| R3 | FastEthernet0/0 | 10.13.0.2/30 | 2001:db8:13::2/64 |
| R3 | FastEthernet0/1 | 10.23.0.2/30 | 2001:db8:23::2/64 |
| R4 | Loopback0 | 10.0.0.4/32 | 2001:db8::4/128 |
| R4 | Loopback1 | 192.168.4.1/24 | — |
| R4 | FastEthernet0/0 | 10.14.0.2/30 | 2001:db8:14::2/64 |

### Cabling Table

| Link ID | Source | Interface | Target | Interface | Subnet IPv4 | Subnet IPv6 |
|---|---|---|---|---|---|---|
| L1 | R1 | Fa0/0 | R2 | Fa0/0 | 10.12.0.0/30 | 2001:db8:12::/64 |
| L2 | R1 | Fa1/0 | R3 | Fa0/0 | 10.13.0.0/30 | 2001:db8:13::/64 |
| L3 | R2 | Fa0/1 | R3 | Fa0/1 | 10.23.0.0/30 | 2001:db8:23::/64 |
| L4 | R1 | Fa1/1 | R4 | Fa0/0 | 10.14.0.0/30 | 2001:db8:14::/64 |

### Console Access Table

| Device | Console Port | Connection Command |
|---|---|---|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |
| R4 | 5004 | `telnet 127.0.0.1 5004` |

---

## 4. Base Configuration

**Initial State:**
- ✅ All routers have hostnames configured
- ✅ All IP addresses (IPv4 and IPv6) are configured on loopbacks and interfaces
- ✅ All loopback interfaces (Lo1, Lo2) on R2, R3, R4 are configured
- ✅ All interfaces are in up/up state
- ✅ `no ip domain-lookup` is configured

**NOT configured (your task):**
- ❌ EIGRP process
- ❌ Network statements (any address family or EIGRP version)
- ❌ Address-family configuration (IPv4, IPv6)
- ❌ Stub routing on R4
- ❌ Manual summarization
- ❌ Route filtering
- ❌ AD manipulation
- ❌ Split horizon control

---

## 5. Lab Challenge: Core Implementation

### Configuration Requirements (No Step-by-Step Guidance Provided)

You must configure the network to meet ALL of the following requirements. No hints or config snippets are provided — use your knowledge from Labs 01–08.

#### Requirement 1: EIGRP Named Mode on All Routers

Configure EIGRP using named mode (not classic mode) on all four routers. Use EIGRP process name `ENARSI` with AS number 100. Both IPv4 and IPv6 address families must be enabled.

#### Requirement 2: Dual-Stack Connectivity (IPv4 and IPv6)

Configure address-family statements for both ipv4 unicast and ipv6 unicast on all routers. Both address families must have full reachability:
- IPv4: 10.0.0.0/8, 172.16.0.0/16, 192.168.0.0/16
- IPv6: 2001:db8::/32

#### Requirement 3: Path Tuning (R1→R3 Preferred from R2)

Manipulate EIGRP metrics so that traffic from R2 to R3 is sent via R1 (Fa0/0 → R1 Fa1/0 → R3) rather than the direct link (R2 Fa0/1 → R3). This may involve modifying bandwidth or delay on interfaces.

#### Requirement 4: R4 Stub Configuration

Configure R4 as an EIGRP stub router using the `connected summary` keyword. R4 must advertise only its own loopbacks and connected subnets, and must NOT be used as a transit router by any other router.

#### Requirement 5: Manual Summarization on R2 and R3

R2 must advertise a single summary route (172.16.20.0/23) covering its two loopbacks (172.16.20.0/24 and 172.16.21.0/24). Similarly, R3 must advertise (172.16.30.0/23) covering its loopbacks. Configure these summaries on the outgoing interfaces toward R1.

#### Requirement 6: Route Filtering on R3

Create a prefix-list and apply a distribute-list on R3 to block R4's loopback (192.168.4.0/24) from being learned. R3 must NOT have a route to 192.168.4.0/24 in its routing table, but R1 and R2 must still have it.

#### Requirement 7: Administrative Distance Manipulation on R1

Modify EIGRP internal AD on R1 to 80 (from default 90). Optionally, configure a floating static route to demonstrate AD influence (not required, but recommended for completeness).

#### Requirement 8: Split Horizon Control on R1

Disable split horizon on R1's Fa0/0 interface (link to R2) to ensure R2 can learn R3's routes via R1, enabling full hub-spoke redundancy.

#### Requirement 9: Variance for Unequal-Cost Load Balancing (Optional but Recommended)

Configure variance on R1 to allow unequal-cost load balancing on suitable routes, demonstrating that multiple paths can be used to increase throughput.

---

## 6. Verification & Analysis

### Verification Checklist

After completing all configuration, verify:

1. **EIGRP Neighbors:**
   ```
   R1# show ip eigrp neighbors
   ! Should show R2, R3, R4 as IPv4 neighbors
   show ipv6 eigrp neighbors
   ! Should show R2, R3, R4 as IPv6 neighbors
   ```

2. **IPv4 Routing Table:**
   ```
   R1# show ip route eigrp
   ! All loopbacks, links, and summaries should appear

   R2# show ip route eigrp
   ! Should include 10.0.0.1, 10.0.0.3, 10.0.0.4, 172.16.30.0/23, 10.13.0.0/30, 10.14.0.0/30
   ! Should NOT include individual 172.16.30 and 172.16.31 (summarized)

   R3# show ip route eigrp
   ! Should include 10.0.0.1, 10.0.0.2, 10.0.0.4, 172.16.20.0/23, 10.12.0.0/30, 10.14.0.0/30
   ! Should NOT include 192.168.4.0/24 (filtered)
   ! Should NOT include individual 172.16.20 and 172.16.21 (summarized)

   R4# show ip route eigrp
   ! All routes learned (R4 is a stub, so receives all but advertises selectively)
   ```

3. **IPv6 Routing Table:**
   ```
   R1# show ipv6 route eigrp
   R2# show ipv6 route eigrp
   ! Full connectivity to all IPv6 loopbacks (2001:db8::/32)
   ```

4. **Path Tuning (R2 to R3 via R1):**
   ```
   R2# show ip route 10.0.0.3
   ! Should show next-hop 10.12.0.1 (R1), metric should be higher than direct link
   ! (or the direct link should be worse due to metric manipulation)
   ```

5. **R4 Stub Status:**
   ```
   R1# show ip eigrp neighbors detail 10.14.0.2
   ! Should show "Stub router"

   R1# show ip eigrp topology 192.168.4.0
   ! Should show route sourced from R4

   R2# show ip route 10.0.0.3
   ! Should not route via R4
   ```

6. **Summarization:**
   ```
   R1# show ip route 172.16.20.0
   ! Should show 172.16.20.0/23, not individual /24s

   R2# show ip route 172.16.20.0
   ! Should show null0 route (discard for summary)

   R1# show ip eigrp topology 172.16.20.0
   ! Should show FD and only the /23 (not /24s)
   ```

7. **Filtering:**
   ```
   R3# show ip route 192.168.4.0
   ! Should be missing (blocked by distribute-list)

   R1# show ip route 192.168.4.0
   R2# show ip route 192.168.4.0
   ! Both should have the route (not filtered)
   ```

8. **AD Modification:**
   ```
   R1# show ip route 10.0.0.2
   ! Should show [80/XXX] (modified AD), not [90/XXX]
   ```

9. **Split Horizon:**
   ```
   R1# show ip split-horizon eigrp 100 Fa0/0
   ! Should show "split horizon is disabled"

   R2# show ip route 10.0.0.3
   ! Should have two next-hops: via R1 (10.12.0.1) and via R3 (10.23.0.2)
   ```

---

## 7. Verification Cheatsheet

| Command | Purpose |
|---|---|
| `show ip eigrp neighbors` | Verify IPv4 EIGRP neighbor adjacencies |
| `show ipv6 eigrp neighbors` | Verify IPv6 EIGRP neighbor adjacencies |
| `show ip route eigrp` | Verify IPv4 routing table (EIGRP routes) |
| `show ipv6 route eigrp` | Verify IPv6 routing table (EIGRP routes) |
| `show ip eigrp topology` | Verify EIGRP topology database |
| `show ip eigrp topology <prefix>` | Inspect one route (FD, RD, successors) |
| `show ip split-horizon eigrp 100 <interface>` | Verify split horizon status |
| `show run \| section eigrp` | View all EIGRP configuration |
| `show ip prefix-list` | Verify prefix-lists (for filtering) |
| `show route-map` | Verify route-maps (if configured) |
| `ping <ipv4> source <ipv4>` | Test IPv4 end-to-end connectivity |
| `ping <ipv6> source <ipv6>` | Test IPv6 end-to-end connectivity |

---

## 8. Solutions (Spoiler Alert!)

> This is a capstone lab — you are expected to work it out independently using your knowledge from Labs 01–08. Attempt all configuration before viewing solutions.

<details>
<summary>Click here ONLY after attempting the entire lab.</summary>

### Complete Configuration Reference

**R1 Configuration:**
```bash
router eigrp ENARSI
 !
 address-family ipv4 unicast autonomous-system 100
  network 10.0.0.1 0.0.0.0
  network 10.12.0.0 0.0.0.3
  network 10.13.0.0 0.0.0.3
  network 10.14.0.0 0.0.0.3
  no auto-summary
  distance eigrp 80 170
  variance 2
  !
  interface FastEthernet0/0
   no ip split-horizon eigrp 100
  !
  topology base
 !
 address-family ipv6 unicast autonomous-system 100
  network 2001:db8::/32
 !
```

**R2 Configuration:**
```bash
router eigrp ENARSI
 !
 address-family ipv4 unicast autonomous-system 100
  network 10.0.0.2 0.0.0.0
  network 10.12.0.0 0.0.0.3
  network 10.23.0.0 0.0.0.3
  network 172.16.20.0 0.0.0.255
  network 172.16.21.0 0.0.0.255
  no auto-summary
  !
  interface FastEthernet0/0
   ip summary-address eigrp 100 172.16.20.0 255.255.254.0
  !
  topology base
 !
 address-family ipv6 unicast autonomous-system 100
  network 2001:db8::/32
 !
```

**R3 Configuration:**
```bash
ip prefix-list BLOCK-R4-LO seq 5 deny 192.168.4.0/24
ip prefix-list BLOCK-R4-LO seq 10 permit 0.0.0.0/0 le 32

router eigrp ENARSI
 !
 address-family ipv4 unicast autonomous-system 100
  network 10.0.0.3 0.0.0.0
  network 10.13.0.0 0.0.0.3
  network 10.23.0.0 0.0.0.3
  network 172.16.30.0 0.0.0.255
  network 172.16.31.0 0.0.0.255
  no auto-summary
  distribute-list prefix-list BLOCK-R4-LO in FastEthernet0/0
  !
  interface FastEthernet0/0
   ip summary-address eigrp 100 172.16.30.0 255.255.254.0
  !
  topology base
 !
 address-family ipv6 unicast autonomous-system 100
  network 2001:db8::/32
 !
```

**R4 Configuration:**
```bash
router eigrp ENARSI
 !
 address-family ipv4 unicast autonomous-system 100
  network 10.0.0.4 0.0.0.0
  network 10.14.0.0 0.0.0.3
  network 192.168.4.0 0.0.0.255
  no auto-summary
  eigrp stub connected summary
  !
  topology base
 !
 address-family ipv6 unicast autonomous-system 100
  network 2001:db8::/32
 !
```

</details>

---

## 9. Troubleshooting Scenarios

You will encounter one or more fault tickets during this lab (similar to previous labs). Each ticket requires you to diagnose and resolve a multi-fault scenario using show commands and your accumulated EIGRP knowledge.

**Example fault scenarios (not exhaustive):**
- Adjacency drops due to AS mismatch or K-value mismatch in address-families
- Incorrect path selection due to metric misconfiguration
- Stub configuration not preventing transit use
- Summarization black hole due to missing loopbacks
- Filtering not applied or applied in wrong direction
- Split horizon still active when it should be disabled

Use all available show commands to diagnose the root cause, then apply fixes systematically.

### Workflow

```bash
python3 setup_lab.py
python3 scripts/fault-injection/inject_scenario_01.py
# Troubleshoot using show commands and knowledge
# Apply fixes to configurations
python3 scripts/fault-injection/apply_solution.py  # Reset between tickets
```

---

## 10. Lab Completion Checklist

**Configuration**
- [ ] EIGRP named mode (ENARSI, AS 100) on all routers
- [ ] IPv4 address-family on all routers with network statements for all prefixes
- [ ] IPv6 address-family on all routers with network statements
- [ ] Loopback1 and Loopback2 on R2 with network statements
- [ ] Loopback1 and Loopback2 on R3 with network statements
- [ ] Loopback1 on R4 with network statement
- [ ] `no auto-summary` on all routers
- [ ] R4 configured as stub: `eigrp stub connected summary`
- [ ] Manual summaries on R2 (Fa0/0) and R3 (Fa0/0)
- [ ] Prefix-list BLOCK-R4-LO on R3 (deny 192.168.4.0/24, permit all)
- [ ] Distribute-list on R3 Fa0/0 inbound (using prefix-list)
- [ ] AD on R1 modified to 80 (or lower)
- [ ] Split horizon disabled on R1 Fa0/0
- [ ] Variance configured on R1 (optional but recommended)
- [ ] Metric tuning to prefer R1→R3 from R2 (bandwidth/delay on interfaces)

**Adjacency & Reachability**
- [ ] R1 has 3 IPv4 EIGRP neighbors (R2, R3, R4)
- [ ] R1 has 3 IPv6 EIGRP neighbors (R2, R3, R4)
- [ ] All IPv4 loopbacks reachable from all routers
- [ ] All IPv6 loopbacks reachable from all routers
- [ ] All link subnets (10.12.0.0, 10.13.0.0, 10.14.0.0, 10.23.0.0) reachable

**Specific Validations**
- [ ] R2 has only 172.16.20.0/23 summary (not individual /24s)
- [ ] R3 has only 172.16.30.0/23 summary (not individual /24s)
- [ ] R3 does NOT have 192.168.4.0/24 (filtered correctly)
- [ ] R1 and R2 DO have 192.168.4.0/24 (unaffected by filtering)
- [ ] R4 is recognized as stub by R1
- [ ] R2 has two next-hops for 10.0.0.3 (via R1 and via R3, due to split horizon disabled)
- [ ] R1 shows [80/XXX] AD for EIGRP routes (modified AD)
- [ ] R1 Fa0/0 shows split horizon disabled

**Troubleshooting**
- [ ] All fault tickets diagnosed and resolved
- [ ] No routes are missing or unreachable
- [ ] All adjacencies stable (no flapping)
- [ ] Topology database complete and consistent

**End-to-End Success**
- [ ] Full IPv4 + IPv6 mesh connectivity
- [ ] All EIGRP concepts from Labs 01–08 are demonstrated
- [ ] No configuration syntax errors
- [ ] All verification cheatsheet commands return expected results
