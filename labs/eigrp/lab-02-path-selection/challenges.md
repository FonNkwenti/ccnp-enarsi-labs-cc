# Troubleshooting Challenges: EIGRP Lab 02

These challenges are designed to test your diagnostic skills. 

**Instructions:**
1. Inject a fault using the corresponding script (e.g., `python3 scripts/fault_inject_1.py`).
2. Identify and resolve the issue on the routers.
3. Once resolved, or to start over, run the refresh script: `python3 scripts/refresh_lab.py`.

## Challenge 1: The Invisible Backup
**Script:** `scripts/fault_inject_1.py`
**Symptom:** You have configured `variance 10` on R1 to enable load balancing to R3 (3.3.3.3/32), but the routing table still only shows one path via R2. You've verified that the redundant link (Fa1/1) is up and EIGRP adjacent.

**Goal:** Identify why the redundant path is not being used for load balancing, even with a high variance. Hint: Check the Feasibility Condition in the topology table.

---

## Challenge 2: Accidental Detour
**Script:** `scripts/fault_inject_2.py`
**Symptom:** Traffic from R1 to R3's loopback (3.3.3.3) is taking a very strange path through another remote site (simulated by high delay on standard links). The primary link is up, but the metric is unexpectedly high.

**Goal:** Find the interface configuration on R1 that has artificially inflated the metric for the primary path.

---

## Challenge 3: Metric Madness
**Script:** `scripts/fault_inject_3.py`
**Symptom:** R1 is no longer learning routes from R3 over the direct link (Fa1/1), although the neighbor relationship is "UP". Pings to R3's interface 10.0.13.2 work, but the 3.3.3.3/32 prefix is only learned via R2.

**Goal:** Investigate why R1 is ignoring the prefix over the direct link. Check for prefix-filtering or offset-lists that might have been applied.

---

## Solutions (Spoiler Alert!)

### Challenge 1: The Invisible Backup — Solution

**Symptom:** `variance 10` is configured on R1 to enable load balancing to R3 (3.3.3.3/32), but the routing table still shows only one path via R2. The redundant link (Fa1/1) is up and EIGRP adjacent.

**Root Cause:** The Feasibility Condition is not met for the path via R3. The Advertised Distance (AD) from R3 must be less than the Feasible Distance (FD) of the successor route for R3 to be considered a Feasible Successor. Without meeting this condition, variance cannot enable load balancing.

**Solution:**

Check the topology table to understand the metric relationship:

```bash
R1# show ip eigrp topology 3.3.3.3/32
EIGRP-IPv4 Topology Entry for AS 100 for 3.3.3.3/32
  State is Passive, Query origin flag is 1, 1 Successor(s), FD is 2688000
  Descriptor Blocks:
  10.0.12.2 (FastEthernet1/0), from 10.0.12.2, Send flag is 0x0
      Composite metric is (2688000/2560000), route is Internal
  10.0.13.2 (FastEthernet1/1), from 10.0.13.2, Send flag is 0x0
      Composite metric is (2752000/2560000), route is Internal
```

The path via R3 (2752000) has an AD of 2560000. Compare with the FD via R2 (2688000). Since 2560000 < 2688000, R3 IS a Feasible Successor. Verify variance is set sufficiently high:

```bash
R1# show ip protocols | include variance
EIGRP metric weight K1=1, K2=0, K3=1, K4=0, K5=0
EIGRP maximum hopcount 100
EIGRP maximum metric variance 10
```

The variance is 10, so routes with metric ≤ (2688000 × 10) = 26880000 should be included. Since 2752000 is within this range, load balancing should work. If it's not appearing in the routing table, check for an `auto-summary` mismatch or verify both neighbors are reachable:

```bash
R1# show ip route 3.3.3.3
Routing Table: VRF default
Codes: C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
       E1 - OSPF external type 1, E2 - OSPF external type 2
       i - IS-IS, su - IS-IS summary, L1 - IS-IS level 1, L2 - IS-IS level 2
       ia - IS-IS inter area, * - candidate default, U - unknown, o - VRF override
       + - replicated route

Routing entry for 3.3.3.3/32
  Known via "eigrp 100", distance 90, metric 2688000, type internal
  Redistributing via eigrp 100
  Last update from 10.0.12.2 on FastEthernet1/0, 00:03:45
  Routing Descriptor Blocks:
  10.0.12.2 (FastEthernet1/0), from 10.0.12.2, metric 2688000, traffic share count is 1
  10.0.13.2 (FastEthernet1/1), from 10.0.13.2, metric 2752000, traffic share count is 1
```

Both paths should now appear with their respective traffic share counts.

---

### Challenge 2: Accidental Detour — Solution

**Symptom:** Traffic from R1 to R3's loopback (3.3.3.3) is taking a strange path through another remote site with high delay. The primary link is up, but the metric is unexpectedly high.

**Root Cause:** The delay on one of the interfaces has been increased (likely on R1 Fa1/0 or R2), causing EIGRP to prefer a different path even though it should be suboptimal.

**Solution:**

Check the interface delays:

```bash
R1# show interface FastEthernet1/0 | include delay
 Encapsulation ARPA, loopback not set
 Keepalive set (10 sec)
 Half-duplex, 100Mb/s, 100BaseTX/FX
 ARP type: ARPA, ARP Timeout 04:00:00
 Last input never, output 00:00:11, output hang never
 Last clearing of "show interface" counters 00:05:22
 Input queue: 0/75/0/0 (size/max/drops/flips); Total output drops: 0
 Queueing strategy: fifo
 Output queue: 0/40 (size/max)
 5 minute input rate 0 bits/sec, 0 output/sec
 5 minute output rate 0 bits/sec, 0 output/sec
    0 packets input, 0 bytes, 0 no buffer
    0 broadcasts, 0 no buffer drops
    0 runts, 0 bits errors, 0 inserted code errors
    0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored, 0 input packet
 100 pps, 100 bits/sec
 Delay: 100 usec
```

The default delay for Fa1/0 is 100 usec. If it's higher, reset it:

```bash
R1# configure terminal
R1(config)# interface FastEthernet1/0
R1(config-if)# no delay
R1(config-if)# exit
R1(config)# end
R1# write memory
```

**Verification:**

```bash
R1# show ip eigrp topology 3.3.3.3/32
EIGRP-IPv4 Topology Entry for AS 100 for 3.3.3.3/32
  State is Passive, Query origin flag is 1, 1 Successor(s), FD is 2688000
  Descriptor Blocks:
  10.0.12.2 (FastEthernet1/0), from 10.0.12.2, Send flag is 0x0
      Composite metric is (2688000/2560000), route is Internal
```

The metric should return to its expected value, and traffic should use the optimal path.

---

### Challenge 3: Metric Madness — Solution

**Symptom:** R1 is no longer learning routes from R3 over the direct link (Fa1/1), although the neighbor relationship is "UP". Pings to R3's interface 10.0.13.2 work, but the 3.3.3.3/32 prefix is only learned via R2.

**Root Cause:** The network statement for the R1-R3 direct link (10.0.13.0/30) is missing or commented out on R3, preventing R3 from advertising the network back to R1.

**Solution:**

Check R3's network statements:

```bash
R3# show running-config | section "router eigrp"
router eigrp 100
 eigrp router-id 3.3.3.3
 network 3.3.3.3 0.0.0.0
 network 10.0.13.0 0.0.0.3
 network 10.0.23.0 0.0.0.3
 passive-interface Loopback0
 no auto-summary
```

If the 10.0.13.0 network statement is missing, add it:

```bash
R3# configure terminal
R3(config)# router eigrp 100
R3(config-router)# network 10.0.13.0 0.0.0.3
R3(config-router)# exit
R3(config)# end
R3# write memory
```

**Verification:**

```bash
R1# show ip eigrp topology 3.3.3.3/32
EIGRP-IPv4 Topology Entry for AS 100 for 3.3.3.3/32
  State is Passive, Query origin flag is 1, 2 Successor(s), FD is 2752000
  Descriptor Blocks:
  10.0.12.2 (FastEthernet1/0), from 10.0.12.2, Send flag is 0x0
      Composite metric is (2688000/2560000), route is Internal
  10.0.13.2 (FastEthernet1/1), from 10.0.13.2, Send flag is 0x0
      Composite metric is (2752000/2560000), route is Internal
```

Both paths to R3 should now be visible in the topology table.
