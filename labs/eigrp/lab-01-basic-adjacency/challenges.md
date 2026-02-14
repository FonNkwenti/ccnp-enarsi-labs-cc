# Troubleshooting Challenges: EIGRP Lab 01

These challenges are designed to test your diagnostic skills. 

**Instructions:**
1. Inject a fault using the corresponding script (e.g., `python3 scripts/fault_inject_1.py`).
2. Identify and resolve the issue on the routers.
3. Once resolved, or to start over, run the refresh script: `python3 scripts/refresh_lab.py`.

## Challenge 1: The "Ghost" Neighbor
**Script:** `scripts/fault_inject_1.py`
**Symptom:** R1 and R2 are connected, but `show ip eigrp neighbors` on R1 shows no neighbors. Pings between the physical interfaces (10.0.12.1 and 10.0.12.2) are successful.

**Goal:** Identify the protocol-level mismatch preventing the adjacency and restore connectivity.

---

## Challenge 2: The Weight of the World (K-Values)
**Script:** `scripts/fault_inject_2.py`
**Symptom:** You see console messages on R2 indicating "K-value mismatch". The adjacency with R3 flap continuously or never establishes.

**Goal:** Determine which K-values are mismatched and reset them to the default enterprise standard.

---

## Challenge 3: Silent Treatment
**Script:** `scripts/fault_inject_3.py`
**Symptom:** R2 shows an adjacency with R3, but R3 shows no neighbors on the link to R2. No EIGRP routes from R2 are appearing in R3's routing table.

**Goal:** Find the interface configuration error on R2 that is suppressing EIGRP Hello packets on a transit link.

---

## Solutions (Spoiler Alert!)

### Challenge 1: The "Ghost" Neighbor — Solution

**Symptom:** R1 and R2 are connected, but `show ip eigrp neighbors` on R1 shows no neighbors. Pings between the physical interfaces are successful.

**Root Cause:** EIGRP is not configured on one of the routers, or the network statement does not include the interconnecting link subnet.

**Solution:**

Verify EIGRP is running and the network statement includes the link:

```bash
R1# show ip protocols
Routing Protocol is "eigrp 100"
Outgoing update filter list for all interfaces is not set
Incoming update filter list for all interfaces is not set
Default networks flagged in outgoing updates
Default networks accepted from incoming updates
EIGRP metric weight K1=1, K2=0, K3=1, K4=0, K5=0
EIGRP maximum hopcount 100
EIGRP maximum metric variance 1
Redistributing: eigrp 100

R1# show running-config | include network
 network 1.1.1.1 0.0.0.0
 network 10.0.12.0 0.0.0.3
```

If the network statement is missing on either R1 or R2, add it:

```bash
R1# configure terminal
R1(config)# router eigrp 100
R1(config-router)# network 10.0.12.0 0.0.0.3
R1(config-router)# exit
R1(config)# end
R1# write memory
```

**Verification:**

```bash
R1# show ip eigrp neighbors
EIGRP-IPv4 Neighbors for AS 100
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   10.0.12.2               Fa1/0                    13 00:02:15   15   200  0  25
```

---

### Challenge 2: The Weight of the World (K-Values) — Solution

**Symptom:** Console messages indicate "K-value mismatch". The adjacency with R3 flaps continuously or never establishes.

**Root Cause:** The K-values (metric weights) are configured differently on R2 than on R3. Default K-values are K1=1, K2=0, K3=1, K4=0, K5=0.

**Solution:**

Verify K-values on both routers:

```bash
R2# show ip eigrp protocols
Routing Protocol is "eigrp 100"
...
EIGRP metric weight K1=1, K2=0, K3=1, K4=0, K5=0

R3# show ip eigrp protocols
Routing Protocol is "eigrp 100"
...
EIGRP metric weight K1=1, K2=0, K3=1, K4=0, K5=0
```

If K-values differ, correct them on R3 (or the router with incorrect values):

```bash
R3# configure terminal
R3(config)# router eigrp 100
R3(config-router)# metric weights 0 1 0 1 0 0
R3(config-router)# exit
R3(config)# end
R3# write memory
```

**Verification:**

After correcting K-values, the adjacency should stabilize:

```bash
R2# show ip eigrp neighbors
EIGRP-IPv4 Neighbors for AS 100
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   10.0.23.2               Fa0/0                    14 00:05:30   20   200  0  18
```

---

### Challenge 3: Silent Treatment — Solution

**Symptom:** R2 shows an adjacency with R3, but R3 shows no neighbors on the link to R2. No EIGRP routes from R2 are appearing in R3's routing table.

**Root Cause:** The EIGRP process is not configured on R3, or passive-interface is incorrectly set on the interconnecting interface.

**Solution:**

Verify R3 has EIGRP configured and the interface is not passive:

```bash
R3# show ip eigrp interfaces
EIGRP-IPv4 Interfaces for AS 100
                        Xmit Queue   PeerQ        Mean   Pacing Time   Multicast    Pending
Interface        Peers  Un/Reliable  Un/Reliable  SRTT   Un/Reliable   Flow Timer   Routes
Fa0/0              1       0/0       0/0           20       0/0           50           0
Lo0                0       0/0       0/0            -         -             -           0
```

If Fa0/0 shows 0 peers, check if it's passive:

```bash
R3# show ip eigrp interfaces Fa0/0 detail
EIGRP-IPv4 Interfaces for AS 100
Fa0/0              0       0/0       0/0           -         -             -           0
  Passive Interface (configured)
```

If passive, remove it:

```bash
R3# configure terminal
R3(config)# router eigrp 100
R3(config-router)# no passive-interface FastEthernet0/0
R3(config-router)# exit
R3(config)# end
R3# write memory
```

**Verification:**

```bash
R3# show ip eigrp neighbors
EIGRP-IPv4 Neighbors for AS 100
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   10.0.23.1               Fa0/0                    11 00:01:45   20   200  0  32

R3# show ip route eigrp
D    1.1.1.1 [90/2816000] via 10.0.23.1, 00:01:40, FastEthernet0/0
D    2.2.2.2 [90/2688000] via 10.0.23.1, 00:01:40, FastEthernet0/0
D    10.0.12.0/30 [90/2816000] via 10.0.23.1, 00:01:40, FastEthernet0/0
```

Routes from R2 should now appear in R3's routing table.
