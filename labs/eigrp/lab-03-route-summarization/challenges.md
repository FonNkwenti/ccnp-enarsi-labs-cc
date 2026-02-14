# Troubleshooting Challenges: EIGRP Lab 03

These challenges are designed to test your diagnostic skills. 

**Instructions:**
1. Inject a fault using the corresponding script (e.g., `python3 scripts/fault_inject_1.py`).
2. Identify and resolve the issue on the routers.
3. Once resolved, or to start over, run the refresh script: `python3 scripts/refresh_lab.py`.

## Challenge 1: The Null0 Blackhole
**Script:** `scripts/fault_inject_1.py`
**Symptom:** R1 has a route for the summarized 172.16.0.0/16 regional network, but it's pointing to `Null0` instead of R7. Consequently, no one can reach the subnets behind R7.

**Goal:** Identify why R1 has locally generated a summary route for a prefix it should be learning from R7, and restore the correct path.

---

## Challenge 2: Summary AD Sabotage
**Script:** `scripts/fault_inject_2.py`
**Symptom:** You've configured summarization on R3, but the summary route is not appearing in the routing tables of R2 or R1. R3's console shows that the neighbor relationship with R2 is stable.

**Goal:** Investigate the administrative distance settings for the summary on R3. Is the summary "too expensive" to be used?

---

## Challenge 3: Overly Aggressive Boundary
**Script:** `scripts/fault_inject_3.py`
**Symptom:** R7 is configured to summarize 172.16.0.0/16, but it is also accidentally summarizing the 10.0.17.0/30 transit link. R1 and R7 have lost their EIGRP adjacency.

**Goal:** Correct the summarization mask or command on R7 to ensure that management and transit networks are not accidentally suppressed by the regional summary.

---

## Solutions (Spoiler Alert!)

### Challenge 1: The Null0 Blackhole — Solution

**Symptom:** R1 has a route for the summarized 172.16.0.0/16 regional network pointing to `Null0` instead of R7. Consequently, no one can reach the subnets behind R7.

**Root Cause:** When a summary route is created on an interface, EIGRP automatically creates a discard route (Null0) pointing to the summary to prevent routing loops. However, the summary route to R7 is not being advertised, only the Null0 discard route is installed locally.

**Solution:**

Verify the configuration on R7:

```bash
R7# show running-config | section "router eigrp"
router eigrp 100
 eigrp router-id 7.7.7.7
 network 7.7.7.7 0.0.0.0
 network 10.0.17.0 0.0.0.3
```

The summary address command is missing. Add it to the interface:

```bash
R7# configure terminal
R7(config)# interface FastEthernet0/0
R7(config-if)# ip summary-address eigrp 100 172.16.0.0 255.255.0.0
R7(config-if)# exit
R7(config)# end
R7# write memory
```

Also ensure the specific subnets (172.16.x.x) are advertised via EIGRP:

```bash
R7# configure terminal
R7(config)# router eigrp 100
R7(config-router)# network 172.16.0.0 0.0.255.255
R7(config-router)# exit
R7(config)# end
R7# write memory
```

**Verification:**

```bash
R1# show ip route eigrp | include 172.16
D    172.16.0.0/16 [90/2870000] via 10.0.17.2, 00:01:30, FastEthernet0/0

R1# ping 172.16.1.1
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 172.16.1.1, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 10/12/15 ms
```

The summary route should now point to R7, not Null0, and subnets should be reachable.

---

### Challenge 2: Summary AD Sabotage — Solution

**Symptom:** Route summarization is configured on R3, but the summary route is not appearing in the routing tables of R2 or R1. R3's neighbor relationship with R2 is stable.

**Root Cause:** The summarized network (192.168.0.0/16) does not exist in R3's routing table, or the specific subnets being summarized are not advertised via EIGRP network statements.

**Solution:**

Check R3's configuration:

```bash
R3# show running-config | section "router eigrp"
router eigrp 100
 eigrp router-id 3.3.3.3
 network 3.3.3.3 0.0.0.0
 network 10.0.23.0 0.0.0.3
 network 10.0.35.0 0.0.0.3
```

Add the networks being summarized:

```bash
R3# configure terminal
R3(config)# router eigrp 100
R3(config-router)# network 192.168.0.0 0.0.255.255
R3(config-router)# exit
R3(config)# end
R3# write memory
```

Add the summary address to the outgoing interface (Fa0/0):

```bash
R3# configure terminal
R3(config)# interface FastEthernet0/0
R3(config-if)# ip summary-address eigrp 100 192.168.0.0 255.255.0.0
R3(config-if)# exit
R3(config)# end
R3# write memory
```

**Verification:**

```bash
R1# show ip route eigrp | include 192.168
D    192.168.0.0/16 [90/2816000] via 10.0.12.2, 00:01:15, FastEthernet1/0

R2# show ip route eigrp | include 192.168
D    192.168.0.0/16 [90/2688000] via 10.0.23.2, 00:00:45, FastEthernet0/1
```

The summary route should now appear in both R1 and R2 routing tables.

---

### Challenge 3: Overly Aggressive Boundary — Solution

**Symptom:** R7 is configured to summarize 172.16.0.0/16, but it is also accidentally summarizing the 10.0.17.0/30 transit link. R1 and R7 have lost their EIGRP adjacency.

**Root Cause:** A summary-address command has been applied that covers both the intended 172.16.x.x subnets AND the transit link 10.0.17.0/30 (e.g., summarizing 10.0.0.0/8 or a broad range that includes 10.0.17.0/30). This prevents the routing protocol from forming an adjacency because the link itself is being summarized away.

**Solution:**

Check the summary address configuration on R7:

```bash
R7# show running-config | include summary-address
ip summary-address eigrp 100 10.0.0.0 255.255.0.0
```

This is too broad and includes the 10.0.17.0/30 transit link. Remove this incorrect summary:

```bash
R7# configure terminal
R7(config)# interface FastEthernet0/0
R7(config-if)# no ip summary-address eigrp 100 10.0.0.0 255.255.0.0
R7(config-if)# exit
R7(config)# end
R7# write memory
```

Add only the correct summary for 172.16.0.0/16:

```bash
R7# configure terminal
R7(config)# interface FastEthernet0/0
R7(config-if)# ip summary-address eigrp 100 172.16.0.0 255.255.0.0
R7(config-if)# exit
R7(config)# end
R7# write memory
```

**Verification:**

```bash
R7# show ip eigrp neighbors
EIGRP-IPv4 Neighbors for AS 100
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   10.0.17.1               FastEthernet0/0         13 00:02:10   15   200  0  22

R1# show ip route eigrp | include 172.16
D    172.16.0.0/16 [90/2870000] via 10.0.17.2, 00:01:30, FastEthernet0/0
```

The adjacency should re-establish, and only the 172.16.0.0/16 summary should be advertised.
