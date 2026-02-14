# Troubleshooting Challenges: EIGRP Lab 10

These challenges are designed to test your diagnostic skills.

**Instructions:**
1. Inject a fault using the corresponding script (e.g., `python3 scripts/fault_inject_1.py`).
2. Identify and resolve the issue on the routers.
3. Once resolved, or to start over, run the refresh script: `python3 scripts/refresh_lab.py`.

## Challenge 1: The Auth Asymmetry
**Script:** `scripts/fault_inject_1.py`
**Symptom:** After configuring SHA-256 authentication on both R1 and R6 for Tunnel8, the EIGRP adjacency over the tunnel drops. `show eigrp address-family ipv4 neighbors` no longer shows the tunnel peer. Debug output mentions "authentication failure".

**Goal:** Investigate the SHA-256 password configured on R6's `af-interface Tunnel8`. Determine if there is a password mismatch and restore the authenticated adjacency.

---

## Challenge 2: The Metric Mismatch
**Script:** `scripts/fault_inject_2.py`
**Symptom:** R1 and R6 have an active EIGRP adjacency, but R1 reports routes from R6 with unexpectedly different metric values. The `show eigrp address-family ipv4 topology` output on R1 shows classic 32-bit metrics for R6 routes, while R1's local routes use 64-bit wide metrics.

**Goal:** Check whether wide metrics (`metric version 64bit`) are still enabled on R6. A version mismatch between peers causes metric translation issues. Restore consistent wide metrics on both sides.

---

## Challenge 3: The Silent Interface
**Script:** `scripts/fault_inject_3.py`
**Symptom:** R1 suddenly loses its EIGRP adjacency with R2 over FastEthernet1/0. `show eigrp address-family ipv4 neighbors` no longer shows R2 as a neighbor. However, R1 can still ping R2's interface address.

**Goal:** Check R1's `af-interface` configuration. Determine if `passive-interface` was accidentally applied to `FastEthernet1/0` instead of `Loopback0`, and correct the configuration.

---

## Solutions (Spoiler Alert!)

### Challenge 1: The Auth Asymmetry — Solution

**Symptom:** After configuring SHA-256 authentication on both R1 and R6 for Tunnel8, the EIGRP adjacency over the tunnel drops.

**Root Cause:** The SHA-256 password on R6 was changed to `WRONG_PASSWORD` instead of matching R1's `SkynetSHA256!`.

**Solution:**

On **R6**, correct the password in the af-interface configuration:

```bash
R6# configure terminal
R6(config)# router eigrp SKYNET_CORE
R6(config-router)# address-family ipv4 autonomous-system 100
R6(config-router-af)# af-interface Tunnel8
R6(config-router-af-interface)# authentication mode hmac-sha-256 SkynetSHA256!
R6(config-router-af-interface)# exit-af-interface
R6(config-router-af)# exit-address-family
R6(config)# end
R6# write memory
```

**Verification:**

```bash
R1# show eigrp address-family ipv4 neighbors detail
EIGRP-IPv4 VR(SKYNET_CORE) Address-Family Neighbors for AS(100)
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   172.16.16.2             Tu8                      12 00:05:22   25   200  0  44
   Version 15.3/3.0, Retrans: 0, Retries: 0, Prefixes: 2
   Authentication SHA-256
```

The adjacency should re-establish with authentication type shown as SHA-256.

---

### Challenge 2: The Metric Mismatch — Solution

**Symptom:** R1 and R6 have an active EIGRP adjacency, but R1 reports routes from R6 with classic 32-bit metrics while R1's local routes use 64-bit wide metrics. This indicates a metric version mismatch.

**Root Cause:** Wide metrics (`metric version 64bit` and `metric rib-scale 128`) were removed from R6's topology base configuration, creating an asymmetry where R1 uses 64-bit and R6 uses classic 32-bit.

**Solution:**

On **R6**, re-enable wide metrics under the topology base:

```bash
R6# configure terminal
R6(config)# router eigrp SKYNET_CORE
R6(config-router)# address-family ipv4 autonomous-system 100
R6(config-router-af)# topology base
R6(config-router-af-topology)# metric version 64bit
R6(config-router-af-topology)# metric rib-scale 128
R6(config-router-af-topology)# exit-af-topology
R6(config-router-af)# exit-address-family
R6(config)# end
R6# write memory
```

**Verification:**

```bash
R1# show eigrp address-family ipv4 topology 6.6.6.6/32
EIGRP-IPv4 VR(SKYNET_CORE) Address-Family Topology Entry for AS(100)/ID(1.1.1.1)
  for 6.6.6.6/32
  State is Passive, Query origin flag is 1, 1 Successor(s), FD is 1966080
  Descriptor Blocks:
  172.16.16.2 (Tunnel8), from 172.16.16.2, Send flag is 0x0
      Composite metric is (1966080/655360), route is Internal
      ...
      Wide metric: [65536/1, 1966080/655360]
```

Wide metrics should now appear in the topology table output, and routes from R6 should match R1's metric format.

---

### Challenge 3: The Silent Interface — Solution

**Symptom:** R1 suddenly loses its EIGRP adjacency with R2 over FastEthernet1/0. R1 can still ping R2's interface address, but `show eigrp address-family ipv4 neighbors` no longer shows R2 as a neighbor.

**Root Cause:** The `passive-interface` command was accidentally applied to `FastEthernet1/0` instead of `Loopback0`. Passive interfaces do not send EIGRP Hello packets, preventing neighbor adjacency formation.

**Solution:**

On **R1**, remove the passive-interface configuration from Fa1/0 and re-apply it to Loopback0:

```bash
R1# configure terminal
R1(config)# router eigrp SKYNET_CORE
R1(config-router)# address-family ipv4 autonomous-system 100
R1(config-router-af)# af-interface FastEthernet1/0
R1(config-router-af-interface)# no passive-interface
R1(config-router-af-interface)# exit-af-interface
R1(config-router-af)# af-interface Loopback0
R1(config-router-af-interface)# passive-interface
R1(config-router-af-interface)# exit-af-interface
R1(config-router-af)# exit-address-family
R1(config)# end
R1# write memory
```

**Verification:**

```bash
R1# show eigrp address-family ipv4 neighbors
EIGRP-IPv4 VR(SKYNET_CORE) Address-Family Neighbors for AS(100)
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   10.0.12.2               Fa1/0                    13 00:02:15   15   200  0  25
```

The R2 neighbor should reappear in the neighbors table. Verify with:

```bash
R1# show eigrp address-family ipv4 interfaces detail FastEthernet1/0
EIGRP-IPv4 VR(SKYNET_CORE) Address-Family Interfaces for AS(100)
                        Xmit Queue   PeerQ        Mean   Pacing Time   Multicast    Pending
Interface        Peers  Un/Reliable  Un/Reliable  SRTT   Un/Reliable   Flow Timer   Routes
Fa1/0              1       0/0       0/0           15       0/0           50           0
  ...
```

Loopback0 should be listed as passive:

```bash
R1# show eigrp address-family ipv4 interfaces detail Loopback0
...
Loopback0          0       0/0       0/0            -         -             -           0
  Passive Interface
```
