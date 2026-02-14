# Troubleshooting Challenges: EIGRP Lab 08

These challenges are designed to test your diagnostic skills. 

**Instructions:**
1. Inject a fault using the corresponding script (e.g., `python3 scripts/fault_inject_1.py`).
2. Identify and resolve the issue on the routers.
3. Once resolved, or to start over, run the refresh script: `python3 scripts/refresh_lab.py`.

## Challenge 1: The Infinite Loop (Recursive Routing)
**Script:** `scripts/fault_inject_1.py`
**Symptom:** You see a console message on R1 or R6 stating "%TUN-5-RECURDOWN: Tunnel8 temporarily disabled due to recursive routing". The EIGRP adjacency never stays UP.

**Goal:** Identify why the router is trying to reach the tunnel destination THROUGH the tunnel itself and fix the EIGRP network advertisements.

---

## Challenge 2: The Giant's Burden (MTU Mismatch)
**Script:** `scripts/fault_inject_2.py`
**Symptom:** Small pings across the tunnel work, but large pings (e.g., `ping 172.16.16.2 size 1500`) fail. EIGRP neighbor status flaps when large routing updates are exchanged.

**Goal:** Correct the IP MTU settings on the tunnel interfaces to account for GRE overhead and ensure large updates can pass.

---

## Challenge 3: Destination Unreachable
**Script:** `scripts/fault_inject_3.py`
**Symptom:** Tunnel8 is "up/down" on R1. `show interface tunnel 8` shows the tunnel is up, but line protocol is down. Pings to the tunnel source/destination physical IPs (10.0.16.x) are failing.

**Goal:** Investigate the physical connectivity or static routing between R1 and R6 that is preventing the tunnel from establishing.

---

## Solutions (Spoiler Alert!)

### Challenge 1: The Infinite Loop (Recursive Routing) — Solution

**Symptom:** Console message appears stating "%TUN-5-RECURDOWN: Tunnel8 temporarily disabled due to recursive routing". The EIGRP adjacency never stays UP.

**Root Cause:** The tunnel destination IP (10.0.16.2) is being learned via EIGRP through the tunnel itself, creating a recursive loop. The router cannot reach the tunnel destination because it's trying to send the traffic through the tunnel.

**Solution:**

Use a static route to the tunnel destination to break the recursion, or configure the tunnel using an interface that is not part of the EIGRP domain:

```bash
R1# configure terminal
R1(config)# ip route 10.0.16.2 255.255.255.255 10.0.16.2
R1(config)# end
R1# write memory
```

Alternatively, use a default route or a summary route for the tunnel destination that is not advertised through the tunnel:

```bash
R1# configure terminal
R1(config)# router eigrp 100
R1(config-router)# no network 10.0.16.0 0.0.0.3
R1(config-router)# exit
R1(config)# end
R1# write memory
```

**Verification:**

```bash
R1# show interface tunnel 8
Tunnel8 is up, line protocol is up
...
```

The tunnel should remain UP, and:

```bash
R1# show ip eigrp neighbors
EIGRP-IPv4 Neighbors for AS 100
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   172.16.16.2             Tu8                    12 00:05:22   25   200  0  44
```

The EIGRP adjacency should stabilize over the tunnel.

---

### Challenge 2: The Giant's Burden (MTU Mismatch) — Solution

**Symptom:** Small pings across the tunnel work, but large pings (e.g., `ping 172.16.16.2 size 1500`) fail. EIGRP neighbor status flaps when large routing updates are exchanged.

**Root Cause:** The tunnel MTU is too large (default 1500), causing packets to be fragmented or dropped. GRE adds 24 bytes of overhead, so the effective MTU should be 1500 - 24 = 1476 at most. EIGRP updates often exceed typical MTU limits and cause the adjacency to flap.

**Solution:**

Set the tunnel MTU to 1400 to account for GRE and IPsec overhead:

```bash
R1# configure terminal
R1(config)# interface Tunnel8
R1(config-if)# ip mtu 1400
R1(config-if)# ip tcp adjust-mss 1360
R1(config-if)# exit
R1(config)# end
R1# write memory
```

Apply the same configuration on R6:

```bash
R6# configure terminal
R6(config)# interface Tunnel8
R6(config-if)# ip mtu 1400
R6(config-if)# ip tcp adjust-mss 1360
R6(config-if)# exit
R6(config)# end
R6# write memory
```

**Verification:**

```bash
R1# show interface tunnel 8 | include MTU
 MTU 1400 bytes, BW 9 Kbit/sec, DLY 50000 usec

R1# ping 172.16.16.2 size 1400
Type escape sequence to abort.
Sending 5, 1400-byte ICMP Echos to 172.16.16.2, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 10/12/15 ms

R1# show ip eigrp neighbors
EIGRP-IPv4 Neighbors for AS 100
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   172.16.16.2             Tu8                    13 00:05:45   20   200  0  50
```

Large packets should now transmit successfully, and the EIGRP adjacency should remain stable.

---

### Challenge 3: Destination Unreachable — Solution

**Symptom:** Tunnel8 is "up/down" on R1. `show interface tunnel 8` shows the tunnel is up, but line protocol is down. Pings to the tunnel source/destination physical IPs (10.0.16.x) are failing.

**Root Cause:** The tunnel source and/or destination addresses are not reachable. This could be due to: (1) a missing route to the tunnel destination, (2) the physical interface (Gi3/0) is down, or (3) firewall/ACL blocking GRE traffic.

**Solution:**

Verify the physical connectivity:

```bash
R1# show interface GigabitEthernet3/0
GigabitEthernet3/0 is up, line protocol is up
```

If the interface is down, enable it:

```bash
R1# configure terminal
R1(config)# interface GigabitEthernet3/0
R1(config-if)# no shutdown
R1(config-if)# exit
R1(config)# end
R1# write memory
```

Verify the tunnel destination is reachable:

```bash
R1# ping 10.0.16.2
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 10.0.16.2, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 5/7/10 ms
```

If pings fail, verify the static route:

```bash
R1# show ip route 10.0.16.2
Routing entry for 10.0.16.2/32
  Known via "connected", distance 0, metric 0 (connected, via interface)
  Routing Descriptor Blocks:
  * directly connected, via GigabitEthernet3/0
      Route metric is 0, traffic share count is 1
```

**Verification:**

```bash
R1# show interface tunnel 8
Tunnel8 is up, line protocol is up
```

The tunnel should now show both "up/up", and:

```bash
R1# show ip eigrp neighbors | grep Tunnel
0   172.16.16.2             Tu8                    13 00:05:30   22   200  0  48
```

The EIGRP adjacency should be stable over the tunnel.
