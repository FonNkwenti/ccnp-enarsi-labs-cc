# Troubleshooting Challenges: EIGRP Lab 09

These challenges are designed to test your diagnostic skills.

**Instructions:**
1. Inject a fault using the corresponding script (e.g., `python3 scripts/fault_inject_1.py`).
2. Identify and resolve the issue on the routers.
3. Once resolved, or to start over, run the refresh script: `python3 scripts/refresh_lab.py`.

## Challenge 1: The Invisible AF (Unicast Routing)
**Script:** `scripts/fault_inject_1.py`
**Symptom:** You've configured Legacy IPv6 EIGRP (`ipv6 router eigrp 100`) on R2 and assigned IPv6 addresses to its interfaces. However, `show ipv6 eigrp neighbors` on R2 is empty, and the router refuses to enter certain IPv6 configuration sub-modes.

**Goal:** Identify the global configuration command missing on R2 that prevents IPv6 routing from functioning entirely.

---

## Challenge 2: Named Mode AS Identity Crisis (R1)
**Script:** `scripts/fault_inject_2.py`
**Symptom:** R1 has full IPv4 adjacencies with all its neighbors, but `show eigrp address-family ipv6 neighbors` on R1 shows an empty table. IPv6 addresses are assigned and `ipv6 unicast-routing` is confirmed active. Pinging IPv6 link-local neighbors directly succeeds.

**Goal:** Inspect the `address-family ipv6` block under `router eigrp SKYNET_CORE` on R1. Check whether the Autonomous System number for the IPv6 address family matches the AS number used by all other routers.

---

## Challenge 3: Tunnel Vision (IPv6 over GRE)
**Script:** `scripts/fault_inject_3.py`
**Symptom:** The GRE tunnel between R1 and R6 is working for IPv4, but EIGRP IPv6 routes from R6 are not appearing on R1. `show ipv6 route eigrp` on R1 shows no routes sourced from R6.

**Goal:** Check the `Tunnel8` interface on R6. Verify that an IPv6 address is assigned and that `ipv6 enable` is present. Ensure the IPv6 address family is active under the Named Mode instance on R6.

---

## Solutions (Spoiler Alert!)

### Challenge 1: The Invisible AF (Unicast Routing) — Solution

**Symptom:** Legacy IPv6 EIGRP is configured on R2 with IPv6 addresses on interfaces, but `show ipv6 eigrp neighbors` is empty and certain IPv6 modes are inaccessible.

**Root Cause:** The global `ipv6 unicast-routing` command is not enabled on R2. Without this, IPv6 forwarding is disabled and the router treats all IPv6 interfaces as down for routing purposes.

**Solution:**

```bash
R2# configure terminal
R2(config)# ipv6 unicast-routing
R2(config)# end
R2# write memory
```

**Verification:**

```bash
R2# show ipv6 eigrp neighbors
EIGRP-IPv6 Neighbors for AS(100)
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   FE80::C801:12FF:FE00:0  Fa0/0                    14 00:02:10   20   200  0  12
1   FE80::C803:23FF:FE00:0  Fa0/1                    11 00:02:05   22   200  0   9
```

IPv6 neighbors should now appear in the neighbors table.

---

### Challenge 2: Named Mode AS Identity Crisis — Solution

**Symptom:** R1's IPv4 adjacencies are stable, but `show eigrp address-family ipv6 neighbors` is empty despite IPv6 being configured and pingable.

**Root Cause:** The `address-family ipv6` block under `router eigrp SKYNET_CORE` on R1 is using a wrong Autonomous System number, causing R1's IPv6 EIGRP to operate on a different AS than all other routers.

**Solution:**

Check the current configuration on R1:

```bash
R1# show running-config | section router eigrp
router eigrp SKYNET_CORE
 address-family ipv4 autonomous-system 100
  ...
 exit-address-family
 !
 address-family ipv6 autonomous-system 666
  ...
 exit-address-family
```

The IPv6 AS is 666 instead of 100. Correct it:

```bash
R1# configure terminal
R1(config)# router eigrp SKYNET_CORE
R1(config-router)# no address-family ipv6 autonomous-system 666
R1(config-router)# address-family ipv6 autonomous-system 100
R1(config-router-af)# topology base
R1(config-router-af-topology)# exit-af-topology
R1(config-router-af)# exit-address-family
R1(config)# end
R1# write memory
```

**Verification:**

```bash
R1# show eigrp address-family ipv6 neighbors
EIGRP-IPv6 VR(SKYNET_CORE) Address-Family Neighbors for AS(100)
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   FE80::C802:12FF:FE34:0  Fa1/0                    14 00:01:15   20   200  0  12
1   FE80::C807:17FF:FE00:0  Fa0/0                    13 00:01:10   18   200  0   8
2   FE80::C806:16FF:FE00:0  Tu8                      12 00:01:05   25   200  0  15
```

All IPv6 adjacencies should reform within 15 seconds.

---

### Challenge 3: Tunnel Vision (IPv6 over GRE) — Solution

**Symptom:** The GRE tunnel works for IPv4, but R6's IPv6 loopback does not appear in R1's routing table via the tunnel.

**Root Cause:** The `Tunnel8` interface on R6 is missing its IPv6 address (`2001:DB8:ACAD:88::2/64`) and `ipv6 enable` has been removed, preventing R6 from sending IPv6 EIGRP hellos over the tunnel.

**Solution:**

```bash
R6# configure terminal
R6(config)# interface Tunnel8
R6(config-if)# ipv6 address 2001:DB8:ACAD:88::2/64
R6(config-if)# ipv6 enable
R6(config-if)# exit
R6(config)# end
R6# write memory
```

**Verification:**

```bash
R1# show ipv6 route eigrp
D   2001:DB8:ACAD:6::6/128 [90/2956800]
     via FE80::C806:16FF:FE00:0, Tunnel8

R1# ping ipv6 2001:DB8:ACAD:6::6
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 2001:DB8:ACAD:6::6, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 20/24/32 ms
```

IPv6 routes from R6 should now appear in R1's routing table via the tunnel.
