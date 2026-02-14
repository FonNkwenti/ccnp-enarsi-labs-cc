# Troubleshooting Challenges: EIGRP Lab 06

These challenges are designed to test your diagnostic skills. 

**Instructions:**
1. Inject a fault using the corresponding script (e.g., `python3 scripts/fault_inject_1.py`).
2. Identify and resolve the issue on the routers.
3. Once resolved, or to start over, run the refresh script: `python3 scripts/refresh_lab.py`.

## Challenge 1: The Recursive Lookup Gap
**Script:** `scripts/fault_inject_1.py`
**Symptom:** R1 neighbor adjacency with R2 is UP, but R1 has NO EIGRP routes in its routing table. You've verified the `AUTHORIZED_NETS` prefix-list is applied.

**Goal:** Identify what is missing from the prefix-list that prevents R1 from installing ANY EIGRP routes. Hint: Think about how EIGRP calculates the next-hop.

---

## Challenge 2: The Implicit Deny Disaster
**Script:** `scripts/fault_inject_2.py`
**Symptom:** R3 has lost all routes from the rest of the network after a "minor" update to the `RM_FILTER_R3` route-map on R2. R3 only sees its locally connected networks.

**Goal:** Fix the route-map on R2 so that it only filters the intended prefix (R1's loopback) and allows everything else.

---

## Challenge 3: Broad Brush Filtering
**Script:** `scripts/fault_inject_3.py`
**Symptom:** R5 can no longer reach R2 or R1's loopbacks, even though the filter was only supposed to block the `10.0.x.x` infrastructure subnets.

**Goal:** Refine the access-list on R3 to ensure it only blocks the intended infrastructure ranges without accidentally catching the management loopbacks.

---

## Solutions (Spoiler Alert!)

### Challenge 1: The Recursive Lookup Gap — Solution

**Symptom:** R1 neighbor adjacency with R2 is UP, but R1 has NO EIGRP routes in its routing table. The `AUTHORIZED_NETS` prefix-list is applied.

**Root Cause:** The distribute-list prefix-list `AUTHORIZED_NETS` is blocking all incoming routes. Either the prefix-list is misconfigured to deny all routes, or the distribute-list is applied in the wrong direction (inbound instead of outbound).

**Solution:**

Check the prefix-list and distribute-list configuration on R1:

```bash
R1# show ip prefix-list AUTHORIZED_NETS
ip prefix-list AUTHORIZED_NETS seq 10 permit 2.2.2.2/32
ip prefix-list AUTHORIZED_NETS seq 20 permit 3.3.3.3/32
ip prefix-list AUTHORIZED_NETS seq 30 permit 10.0.23.0/30
ip prefix-list AUTHORIZED_NETS seq 40 permit 10.5.0.0/16
ip prefix-list AUTHORIZED_NETS seq 50 deny any

R1# show running-config | include distribute-list
 distribute-list prefix-list AUTHORIZED_NETS in FastEthernet1/0
```

The issue is that the prefix-list may be too restrictive or the distribute-list is applied in the wrong direction. If filtering is needed, ensure the prefix-list permits the necessary routes. Apply filters on the **outbound** direction (where routes originate) rather than inbound to avoid filtering:

```bash
R1# configure terminal
R1(config)# router eigrp 100
R1(config-router)# no distribute-list prefix-list AUTHORIZED_NETS in FastEthernet1/0
R1(config-router)# exit
R1(config)# end
R1# write memory
```

**Verification:**

```bash
R1# show ip route eigrp
D    2.2.2.2/32 [90/2688000] via 10.0.12.2, 00:01:15, FastEthernet1/0
D    3.3.3.3/32 [90/2816000] via 10.0.12.2, 00:01:15, FastEthernet1/0
D    10.0.23.0/30 [90/2816000] via 10.0.12.2, 00:01:15, FastEthernet1/0
D    10.5.0.0/16 [90/2816000] via 10.0.12.2, 00:01:15, FastEthernet1/0
D    5.5.5.5/32 [90/2816000] via 10.0.12.2, 00:01:15, FastEthernet1/0
```

EIGRP routes should now appear in R1's routing table.

---

### Challenge 2: The Implicit Deny Disaster — Solution

**Symptom:** R3 has lost all routes from the rest of the network after an update to the `RM_FILTER_R3` route-map on R2. R3 only sees its locally connected networks.

**Root Cause:** The route-map `RM_FILTER_R3` on R2 has a permit clause that matches R1's loopback (1.1.1.1), but subsequent clauses or a missing final permit statement are denying all other routes.

**Solution:**

Check the route-map on R2:

```bash
R2# show route-map RM_FILTER_R3
route-map RM_FILTER_R3, permit, sequence 10
  Match clauses:
    ip address prefix-list R1_LOOP
  Set clauses:
  Policy routing matches: 0 packets, 0 bytes
route-map RM_FILTER_R3, deny, sequence 20
  Match clauses:
  Set clauses:
  Policy routing matches: 0 packets, 0 bytes
```

The route-map has a deny clause (sequence 20) without match conditions, which implicitly denies all other routes. Replace it with a permit clause:

```bash
R2# configure terminal
R2(config)# route-map RM_FILTER_R3 permit 20
R2(config-route-map)# exit
R2(config)# end
R2# write memory
```

**Verification:**

```bash
R3# show ip route eigrp
D    1.1.1.1/32 [90/2816000] via 10.0.23.1, 00:01:15, FastEthernet0/0
D    2.2.2.2/32 [90/2688000] via 10.0.23.1, 00:01:15, FastEthernet0/0
D    10.0.12.0/30 [90/2816000] via 10.0.23.1, 00:01:15, FastEthernet0/0
```

R3 should now receive all routes from R1 and R2.

---

### Challenge 3: Broad Brush Filtering — Solution

**Symptom:** R5 can no longer reach R2 or R1's loopbacks, even though the filter was only supposed to block the `10.0.x.x` infrastructure subnets.

**Root Cause:** The access-list or route-map filtering on R3 is too broad and is filtering loopback addresses (2.2.2.2, 1.1.1.1) in addition to infrastructure subnets.

**Solution:**

Check the filtering configuration on R3:

```bash
R3# show running-config | section "router eigrp"
router eigrp 100
 distribute-list 66 out FastEthernet0/1

R3# show access-lists 66
Standard IP access list 66
    10 deny 10.0.0.0 0.255.255.255
    20 permit any
```

The access-list is correct (denies 10.0.x.x, permits everything else). However, if R5 is still not receiving loopbacks, verify the distribution:

```bash
R3# show ip route eigrp
D    1.1.1.1/32 [90/2816000] via 10.0.23.1, 00:01:45, FastEthernet0/0
D    2.2.2.2/32 [90/2688000] via 10.0.23.1, 00:01:45, FastEthernet0/0
```

Verify R5 has the correct network statements to receive routes:

```bash
R5# show running-config | section "router eigrp"
router eigrp 100
 network 5.5.5.5 0.0.0.0
 network 10.0.35.0 0.0.0.3
 eigrp stub connected summary
```

R5 needs to have passive-interface configured on non-EIGRP interfaces and should receive all advertised routes:

```bash
R5# show ip route eigrp
D    1.1.1.1/32 [90/2816000] via 10.0.35.1, 00:02:15, FastEthernet0/0
D    2.2.2.2/32 [90/2816000] via 10.0.35.1, 00:02:15, FastEthernet0/0
```

The loopback addresses should now be reachable from R5, while infrastructure routes remain filtered.
