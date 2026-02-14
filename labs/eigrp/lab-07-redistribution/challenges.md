# Troubleshooting Challenges: EIGRP Lab 07

These challenges are designed to test your diagnostic skills. 

**Instructions:**
1. Inject a fault using the corresponding script (e.g., `python3 scripts/fault_inject_1.py`).
2. Identify and resolve the issue on the routers.
3. Once resolved, or to start over, run the refresh script: `python3 scripts/refresh_lab.py`.

## Challenge 1: The Infinite Distance (Seed Metrics)
**Script:** `scripts/fault_inject_1.py`
**Symptom:** R1 is successfully learning CyberDyne (OSPF) routes, but R2 and R3 have no external (D EX) routes in their routing tables. R1's `router eigrp 100` configuration shows redistribution is active.

**Goal:** Identify why the OSPF routes are not being propagated into the EIGRP domain and fix the metric issue.

---

## Challenge 2: Tagged Out (Redistribution Loop Prevention)
**Script:** `scripts/fault_inject_2.py`
**Symptom:** You've implemented a complex route-map to prevent loops, but now R4 (OSPF) is not receiving any Skynet routes. You see tag `222` in the configuration, but no external LSAs on R4.

**Goal:** Determine if the loop-prevention route-map is being too restrictive and blocking legitimate redistribution.

---

## Challenge 3: Subnet Scarcity
**Script:** `scripts/fault_inject_3.py`
**Symptom:** R4 can reach R1's directly connected interfaces, but it cannot see the EIGRP loopbacks (2.2.2.2, 3.3.3.3) or the stub networks. 

**Goal:** Find the missing keyword in the OSPF redistribution command on R1 that is preventing classless subnets from being advertised.

---

## Solutions (Spoiler Alert!)

### Challenge 1: The Infinite Distance (Seed Metrics) — Solution

**Symptom:** R1 is successfully learning CyberDyne (OSPF) routes, but R2 and R3 have no external (D EX) routes in their routing tables. R1's `router eigrp 100` configuration shows redistribution is active.

**Root Cause:** The redistribute command on R1 is missing the `metric` parameter, so OSPF routes are being redistributed with an infinite metric (unreachable) and are not propagated to other EIGRP routers.

**Solution:**

Check the redistribute configuration on R1:

```bash
R1# show running-config | section "router eigrp"
router eigrp 100
 redistribute ospf 1
```

Add the metric parameters (K-values: bandwidth, delay, reliability, load, MTU):

```bash
R1# configure terminal
R1(config)# router eigrp 100
R1(config-router)# redistribute ospf 1 metric 10000 100 255 1 1500
R1(config-router)# exit
R1(config)# end
R1# write memory
```

**Verification:**

```bash
R2# show ip route eigrp | include EX
D EX 4.4.4.4/32 [170/2956800] via 10.0.12.1, 00:01:15, FastEthernet0/0

R3# show ip route eigrp | include EX
D EX 4.4.4.4/32 [170/2834800] via 10.0.23.1, 00:01:30, FastEthernet0/0
```

OSPF routes should now appear as external EIGRP routes (D EX) in R2 and R3.

---

### Challenge 2: Tagged Out (Redistribution Loop Prevention) — Solution

**Symptom:** A complex route-map is implemented to prevent loops, but R4 (OSPF) is not receiving any Skynet routes. Tag `222` is in the configuration, but no external LSAs on R4.

**Root Cause:** The route-map used in the `redistribute eigrp` statement on R1 is incorrectly filtering all EIGRP routes, or the route-map match condition is too restrictive.

**Solution:**

Check the route-map on R1:

```bash
R1# show route-map EIGRP_TO_OSPF
route-map EIGRP_TO_OSPF, permit, sequence 10
  Match clauses:
    tag 222
  Set clauses:
    tag 333
  Policy routing matches: 0 packets, 0 bytes
route-map EIGRP_TO_OSPF, deny, sequence 20
  Match clauses:
  Set clauses:
  Policy routing matches: 0 packets, 0 bytes
```

The route-map is matching only routes with tag 222 (which don't exist yet because they haven't been created). Change the match condition to permit all EIGRP routes:

```bash
R1# configure terminal
R1(config)# route-map EIGRP_TO_OSPF permit 10
R1(config-route-map)# no match tag 222
R1(config-route-map)# exit
R1(config)# route-map EIGRP_TO_OSPF permit 20
R1(config-route-map)# exit
R1(config)# end
R1# write memory
```

**Verification:**

```bash
R4# show ip route ospf | include E1
O E1 1.1.1.1/32 [110/2856] via 10.0.14.1, 00:01:15, FastEthernet0/0
O E1 2.2.2.2/32 [110/2728] via 10.0.14.1, 00:01:15, FastEthernet0/0
O E1 3.3.3.3/32 [110/2856] via 10.0.14.1, 00:01:15, FastEthernet0/0
```

EIGRP routes should now appear as external OSPF routes (O E1) on R4.

---

### Challenge 3: Subnet Scarcity — Solution

**Symptom:** R4 can reach R1's directly connected interfaces, but it cannot see the EIGRP loopbacks (2.2.2.2, 3.3.3.3) or the stub networks.

**Root Cause:** The redistribute command is missing the `subnets` keyword in the OSPF redistribution, so only summarized routes (not individual subnets) are being advertised.

**Solution:**

Check the OSPF configuration on R1:

```bash
R1# show running-config | section "router ospf"
router ospf 1
 redistribute eigrp 100 route-map EIGRP_TO_OSPF
```

Add the `subnets` keyword to permit redistribution of host routes and subnets:

```bash
R1# configure terminal
R1(config)# router ospf 1
R1(config-router)# redistribute eigrp 100 route-map EIGRP_TO_OSPF subnets
R1(config-router)# exit
R1(config)# end
R1# write memory
```

**Verification:**

```bash
R4# show ip route ospf
O E1 1.1.1.1/32 [110/2856] via 10.0.14.1, 00:01:15, FastEthernet0/0
O E1 2.2.2.2/32 [110/2728] via 10.0.14.1, 00:01:15, FastEthernet0/0
O E1 3.3.3.3/32 [110/2856] via 10.0.14.1, 00:01:15, FastEthernet0/0
O E1 5.5.5.5/32 [110/2856] via 10.0.14.1, 00:01:15, FastEthernet0/0
O E1 10.0.23.0/30 [110/2856] via 10.0.14.1, 00:01:15, FastEthernet0/0
O E1 10.0.35.0/30 [110/2856] via 10.0.14.1, 00:01:15, FastEthernet0/0
```

All EIGRP routes including loopbacks and subnets should now be visible on R4.
