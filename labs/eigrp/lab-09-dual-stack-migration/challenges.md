# Troubleshooting Challenges: EIGRP Lab 09

These challenges are designed to test your diagnostic skills. 

**Instructions:**
1. Inject a fault using the corresponding script (e.g., `python3 scripts/fault_inject_1.py`).
2. Identify and resolve the issue on the routers.
3. Once resolved, or to start over, run the refresh script: `python3 scripts/refresh_lab.py`.

## Challenge 1: The Invisible AF (Unicast Routing)
**Script:** `scripts/fault_inject_1.py`
**Symptom:** You've configured the EIGRP Named Mode `address-family ipv6` on R1 and R2, and assigned IPv6 addresses to the interfaces. However, `show ipv6 eigrp neighbors` is empty, and the router won't even let you enter certain IPv6 configuration modes.

**Goal:** Identify the global configuration command missing on R2 that prevents IPv6 routing from functioning.

---

## Challenge 2: Named Mode Identity Crisis
**Script:** `scripts/fault_inject_2.py`
**Symptom:** R1 and R2 have established an IPv4 adjacency, but the IPv6 adjacency won't form. `show eigrp address-family ipv6 neighbors` shows nothing. You've verified physical and IPv6 connectivity (pings work).

**Goal:** Investigate the `address-family` configuration under the Named Mode process on R2. Is the Autonomous System number correct for the IPv6 family?

---

## Challenge 3: Tunnel Vision (IPv6 over GRE)
**Script:** `scripts/fault_inject_3.py`
**Symptom:** The GRE tunnel between R1 and R6 is working for IPv4, but EIGRP IPv6 routes from R6 are not appearing on R1. `show ipv6 route eigrp` on R1 shows no routes via the tunnel.

**Goal:** Check the tunnel interface configuration on R6. Ensure IPv6 is properly enabled and that the tunnel is correctly participating in the IPv6 address family.

---

## Solutions (Spoiler Alert!)

### Challenge 1: The Invisible AF (Unicast Routing) — Solution

**Symptom:** EIGRP Named Mode `address-family ipv6` is configured on R1 and R2 with IPv6 addresses assigned to interfaces. However, `show ipv6 eigrp neighbors` is empty, and the router won't allow certain IPv6 configuration modes.

**Root Cause:** The global `ipv6 unicast-routing` command is not enabled on one or both routers. Without this, IPv6 forwarding is disabled, and the router treats IPv6 interfaces as down for routing purposes.

**Solution:**

Enable IPv6 unicast routing globally on both R1 and R2:

```bash
R1# configure terminal
R1(config)# ipv6 unicast-routing
R1(config)# end
R1# write memory

R2# configure terminal
R2(config)# ipv6 unicast-routing
R2(config)# end
R2# write memory
```

**Verification:**

```bash
R1# show ipv6 eigrp neighbors
EIGRP-IPv6 VR(SKYNET_CORE) Address-Family Neighbors for AS(100)
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   FE80::C802:12FF:FE34:0  Fa1/0                    14 00:05:12   20   200  0  12
```

IPv6 neighbors should now appear in the neighbors table.

---

### Challenge 2: Named Mode Identity Crisis — Solution

**Symptom:** R1 and R2 have established an IPv4 adjacency, but the IPv6 adjacency won't form. `show eigrp address-family ipv6 neighbors` shows nothing. Physical and IPv6 connectivity work (pings succeed).

**Root Cause:** The IPv6 address-family is not configured under the Named Mode instance with the same AS number. The IPv4 AS is 100, but the IPv6 AS may be misconfigured or missing entirely.

**Solution:**

Check the EIGRP configuration on R2:

```bash
R2# show running-config | section "router eigrp"
router eigrp SKYNET_CORE
 address-family ipv4 autonomous-system 100
  ...
 exit-address-family
 !
 address-family ipv6 autonomous-system 200
  ...
 exit-address-family
```

The IPv6 AS is 200 instead of 100. Correct it:

```bash
R2# configure terminal
R2(config)# router eigrp SKYNET_CORE
R2(config-router)# no address-family ipv6 autonomous-system 200
R2(config-router)# address-family ipv6 autonomous-system 100
R2(config-router-af)# topology base
R2(config-router-af-topology)# exit-af-topology
R2(config-router-af)# exit-address-family
R2(config)# end
R2# write memory
```

**Verification:**

```bash
R1# show eigrp address-family ipv6 neighbors
EIGRP-IPv6 VR(SKYNET_CORE) Address-Family Neighbors for AS(100)
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   FE80::C802:23FF:FE34:1  Fa1/0                    14 00:05:30   18   200  0  15
```

IPv6 adjacencies should now form.

---

### Challenge 3: Tunnel Vision (IPv6 over GRE) — Solution

**Symptom:** The GRE tunnel between R1 and R6 works for IPv4, but EIGRP IPv6 routes from R6 are not appearing on R1. `show ipv6 route eigrp` on R1 shows no routes via the tunnel.

**Root Cause:** The tunnel interface does not have an IPv6 address configured, or the IPv6 address-family is not configured on the tunnel interface in the EIGRP process.

**Solution:**

Check the tunnel configuration on R6:

```bash
R6# show interface Tunnel8
Tunnel8 is up, line protocol is up
 Internet address is 172.16.16.2, 0x1
 (no IPv6 address assigned)
```

Add an IPv6 address to the tunnel:

```bash
R6# configure terminal
R6(config)# interface Tunnel8
R6(config-if)# ipv6 address 2001:DB8:ACAD:88::2/64
R6(config-if)# ipv6 enable
R6(config-if)# exit
R6(config)# end
R6# write memory
```

Verify EIGRP is advertising the tunnel in the IPv6 address-family. Ensure the network statement includes the tunnel subnet:

```bash
R6# show running-config | section "router eigrp"
router eigrp SKYNET_CORE
 address-family ipv6 autonomous-system 100
  ...
```

If there's no network statement for the tunnel, the tunnel won't be advertised. Add it if missing:

```bash
R6# configure terminal
R6(config)# router eigrp SKYNET_CORE
R6(config-router)# address-family ipv6 autonomous-system 100
R6(config-router-af)# network 2001:DB8:ACAD:88::/64
R6(config-router-af)# exit-address-family
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

IPv6 routes from R6 should now appear in R1's routing table.
