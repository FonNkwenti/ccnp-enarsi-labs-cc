# Troubleshooting Challenges: EIGRP Lab 04

These challenges are designed to test your diagnostic skills. 

**Instructions:**
1. Inject a fault using the corresponding script (e.g., `python3 scripts/fault_inject_1.py`).
2. Identify and resolve the issue on the routers.
3. Once resolved, or to start over, run the refresh script: `python3 scripts/refresh_lab.py`.

## Challenge 1: The "Receive-Only" Silence
**Script:** `scripts/fault_inject_1.py`
**Symptom:** R3 is adjacent with R5, but R1 and R2 no longer have any routes to the 10.5.x.x networks located behind R5. R5's neighbor status on R3 shows it is a "Stub Peer".

**Goal:** Identify why R5 has stopped advertising its connected networks and restore reachability while keeping R5 as a stub.

---

## Challenge 2: The WAN Timeout
**Script:** `scripts/fault_inject_2.py`
**Symptom:** The EIGRP adjacency between R1 and R2 is constantly flapping. You see logs indicating that the neighbor has been "reset" due to "hold timer expired". You've verified the physical link is stable.

**Goal:** Compare the EIGRP hello and hold timers on both sides of the R1-R2 WAN link and ensure they are consistent and appropriate for a slow leased line.

---

## Challenge 3: Forgotten Static Routes
**Script:** `scripts/fault_inject_3.py`
**Symptom:** R5 has a static route to a legacy server at 192.168.99.1. Management wants this route to be shared with the rest of the company, but despite having `eigrp stub connected summary`, the static route is not appearing in R1's routing table.

**Goal:** Modify the stub configuration on R5 to allow the advertisement of static routes, without removing the stub protection.

---

## Solutions (Spoiler Alert!)

### Challenge 1: The "Receive-Only" Silence — Solution

**Symptom:** R3 is adjacent with R5 and R5's neighbor status shows it is a "Stub Peer", but R1 and R2 no longer have any routes to the 10.5.x.x networks located behind R5.

**Root Cause:** The stub configuration on R5 is missing the `connected` keyword, so connected routes (10.5.x.x subnets) are not being redistributed and advertised to the core network.

**Solution:**

Check R5's EIGRP configuration:

```bash
R5# show running-config | section "router eigrp"
router eigrp 100
 eigrp router-id 5.5.5.5
 network 5.5.5.5 0.0.0.0
 network 10.0.35.0 0.0.0.3
 eigrp stub summary
```

Add the `connected` keyword to the stub configuration:

```bash
R5# configure terminal
R5(config)# router eigrp 100
R5(config-router)# eigrp stub connected summary
R5(config-router)# exit
R5(config)# end
R5# write memory
```

Also, ensure the 10.5.x.x networks are advertised:

```bash
R5# configure terminal
R5(config)# router eigrp 100
R5(config-router)# network 10.5.0.0 0.0.255.255
R5(config-router)# exit
R5(config)# end
R5# write memory
```

**Verification:**

```bash
R1# show ip route eigrp | include 10.5
D    10.5.0.0/16 [90/2816000] via 10.0.12.2, 00:01:15, FastEthernet1/0

R2# show ip route eigrp | include 10.5
D    10.5.0.0/16 [90/2688000] via 10.0.23.2, 00:00:45, FastEthernet0/1
```

Routes from R5 should now appear in R1 and R2 routing tables.

---

### Challenge 2: The WAN Timeout — Solution

**Symptom:** The EIGRP adjacency between R1 and R2 is constantly flapping with logs indicating the neighbor has been "reset" due to "hold timer expired". The physical link is stable.

**Root Cause:** The hello/hold timers are configured asymmetrically between R1 and R2. EIGRP requires matching timers to maintain adjacency. The default is hello=5s, hold=15s. If one side has longer timers (e.g., hello=60s, hold=180s), the other side's hold timer may expire before the hello is received.

**Solution:**

Check the current timers on both routers:

```bash
R1# show ip eigrp interfaces detail FastEthernet1/0
EIGRP-IPv4 Interfaces for AS 100
                        Xmit Queue   PeerQ        Mean   Pacing Time   Multicast    Pending
Interface        Peers  Un/Reliable  Un/Reliable  SRTT   Un/Reliable   Flow Timer   Routes
Fa1/0              1       0/0       0/0           15       0/0           50           0
  Hello-interval is 5, Hold-time is 15

R2# show ip eigrp interfaces detail FastEthernet0/0
EIGRP-IPv4 Interfaces for AS 100
                        Xmit Queue   PeerQ        Mean   Pacing Time   Multicast    Pending
Interface        Peers  Un/Reliable  Un/Reliable  SRTT   Un/Reliable   Flow Timer   Routes
Fa0/0              1       0/0       0/0           20       0/0           50           0
  Hello-interval is 60, Hold-time is 180
```

The timers are asymmetrical. Configure matching timers on R1:

```bash
R1# configure terminal
R1(config)# interface FastEthernet1/0
R1(config-if)# ip hello-interval eigrp 100 60
R1(config-if)# ip hold-time eigrp 100 180
R1(config-if)# exit
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

The neighbor adjacency should stabilize and no longer flap.

---

### Challenge 3: Forgotten Static Routes — Solution

**Symptom:** R5 has a static route to a legacy server at 192.168.99.1. Despite having `eigrp stub connected summary`, the static route is not appearing in R1's routing table.

**Root Cause:** The `eigrp stub connected summary` configuration only redistributes **connected routes** (routes from configured network statements) and **summaries**. Static routes are not automatically included. To advertise static routes, they must be redistributed into EIGRP.

**Solution:**

Add a network statement to include the static route's subnet, or use redistribution. For this scenario, use a static route to Null0 as a summary and then redistribute static routes:

```bash
R5# configure terminal
R5(config)# ip route 192.168.99.0 255.255.255.0 <next-hop>
R5(config)# router eigrp 100
R5(config-router)# redistribute static
R5(config-router)# exit
R5(config)# end
R5# write memory
```

Alternatively, create a summary route for the static destination and advertise it:

```bash
R5# configure terminal
R5(config)# interface FastEthernet0/0
R5(config-if)# ip summary-address eigrp 100 192.168.99.0 255.255.255.0
R5(config-if)# exit
R5(config)# end
R5# write memory
```

**Verification:**

```bash
R1# show ip route eigrp | include 192.168
D    192.168.99.0/24 [90/2816000] via 10.0.12.2, 00:01:15, FastEthernet1/0

R1# ping 192.168.99.1
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 192.168.99.1, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 20/25/30 ms
```

The static route to the legacy server should now be reachable across the EIGRP network.
