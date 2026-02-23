# EIGRP Lab 02: Named Mode & Dual-Stack IPv6 Address Family

## 1. Concepts & Skills Covered

**Exam Bullets:**
- 1.9.a Address families (IPv4, IPv6)
- 1.9.b Neighbor adjacency

**What You'll Learn:**
- The difference between EIGRP classic mode and named mode (router eigrp AS vs. router eigrp NAME)
- How to configure dual address families (IPv4 and IPv6) in named mode
- How to verify both IPv4 and IPv6 neighbor adjacencies and routing tables
- Why K-values must match between address families
- Troubleshooting IPv6 unicast routing and address family misconfigurations

**Key Concepts:**
- **Named Mode**: More flexible, supports multiple address families, easier to manage complex deployments
- **Address Family Context**: Each AF (IPv4, IPv6) maintains separate neighbor adjacencies, topology tables, and routing tables
- **K-Values**: Must match between all address families on neighboring routers; default is K1=1, K3=1, K2=0, K4=0, K5=0
- **IPv6 Routing**: Requires `ipv6 unicast-routing` globally; EIGRP uses link-local addresses for hellos

---

## 2. Topology & Scenario

**Enterprise Context:**
Acme Corp is standardizing its routing infrastructure. The network was initially deployed with EIGRP classic mode (Lab 01 state). The operations team is now migrating to named mode to prepare for future multi-protocol deployments and to enable IPv6 support across the WAN.

You are the network engineer tasked with:
1. Migrating all three routers from classic mode to named mode (without disrupting existing IPv4 traffic)
2. Adding IPv6 address family to all routers
3. Verifying that both IPv4 and IPv6 neighbors form adjacencies
4. Troubleshooting any misconfigurations that prevent dual-stack operation

**Topology (unchanged from Lab 01):**

```
              ┌─────────────────────────┐
              │           R1            │
              │    (Hub / Core)         │
              │ Lo0: 10.0.0.1/32        │
              │ Lo0: 2001:db8::1/128    │
              └──────┬───────────┬──────┘
           Fa0/0     │           │     Fa1/0
     10.12.0.1/30    │           │   10.13.0.1/30
   2001:db8:12::1/64 │           │ 2001:db8:13::1/64
                     │           │
     10.12.0.2/30    │           │   10.13.0.2/30
   2001:db8:12::2/64 │           │ 2001:db8:13::2/64
           Fa0/0     │           │     Fa0/0
     ┌───────────────┘           └───────────────┐
     │                                           │
┌────┴──────────────┐           ┌────────────────┴────┐
│       R2          │           │       R3            │
│   (Branch A)      │           │   (Branch B)        │
│ Lo0: 10.0.0.2/32  │           │ Lo0: 10.0.0.3/32    │
│2001:db8::2/128    │           │2001:db8::3/128      │
└──────────┬────────┘           └─────────┬───────────┘
      Fa0/1│                              │Fa0/1
10.23.0.1/30│                            │10.23.0.2/30
2001:db8:23::1/64                        2001:db8:23::2/64
            └────────────────────────────┘
                   10.23.0.0/30
              2001:db8:23::/64
```

---

## 3. Hardware & Environment Specifications

**Devices:**

| Device | Platform | Role | Console Port |
|--------|----------|------|--------------|
| R1 | c7200 | Hub / Core | 5001 |
| R2 | c3725 | Branch A | 5002 |
| R3 | c3725 | Branch B | 5003 |

**Cabling Table:**

| Link ID | Source Interface | Target Interface | Subnet (IPv4) | Subnet (IPv6) |
|---------|------------------|------------------|---------------|---------------|
| L1 | R1 Fa0/0 | R2 Fa0/0 | 10.12.0.0/30 | 2001:db8:12::/64 |
| L2 | R1 Fa1/0 | R3 Fa0/0 | 10.13.0.0/30 | 2001:db8:13::/64 |
| L3 | R2 Fa0/1 | R3 Fa0/1 | 10.23.0.0/30 | 2001:db8:23::/64 |

**Console Access Table:**

| Device | Port | Connection Command |
|--------|------|---------------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |

---

## 4. Base Configuration

**What is Pre-Configured (from Lab 01):**

All three routers are running **EIGRP classic mode (AS 100)** with IPv4 adjacencies already formed and stable.

```
R1, R2, R3:
- router eigrp 100
- network 10.0.0.0 0.0.0.255
- network 10.12.0.0 0.0.0.3
- network 10.13.0.0 0.0.0.3
- network 10.23.0.0 0.0.0.3
- no auto-summary
- (IPv6 not configured yet)
```

**What You'll Add in This Lab:**

- Global IPv6 unicast routing
- Named mode EIGRP (router eigrp ENARSI)
- Address family ipv4 unicast with AS 100
- Address family ipv6 unicast with AS 100
- Network statements for both IPv4 and IPv6
- IPv6 addresses on all interfaces and loopbacks

---

## 5. Lab Challenge: Core Implementation

You have one maintenance window to migrate the network from classic to named mode and enable IPv6. The classic configuration must remain stable during the migration, and both address families must form neighbors before the window closes.

### Objective 1: Enable IPv6 Routing

On **all three routers**, enable IPv6 unicast routing globally.

**Verification:** `show ipv6 route` should show local IPv6 routes (not empty).

### Objective 2: Migrate to Named Mode on R1

On **R1 only**, perform the migration from classic to named mode:
1. Remove the `router eigrp 100` classic configuration
2. Configure `router eigrp ENARSI`
3. Add `address-family ipv4 unicast` with `autonomous-system 100`
4. Add network statements for IPv4
5. Add `address-family ipv6 unicast` with `autonomous-system 100`
6. Add IPv6 network statements

**Do not configure R2 or R3 yet** — only R1. This tests your understanding of name-mode syntax.

**Verification (R1 only):**
- `show ip eigrp neighbors` — should show R2 and R3 still (classic adjacency stays until they migrate)
- `show ipv6 eigrp neighbors` — should be empty (R2 and R3 haven't migrated to named mode yet)

### Objective 3: Migrate to Named Mode on R2 and R3

Perform the same migration on **R2** and **R3**.

**Verification after both migrate:**
- `show ip eigrp neighbors` — should show both peers under named mode context
- `show ipv6 eigrp neighbors` — should show R1 and R3 (for R2); R1 and R2 (for R3) with link-local addresses
- `show ip route eigrp` — all learned routes should be present
- `show ipv6 route eigrp` — all learned IPv6 routes should be present

### Objective 4: Verify Full Dual-Stack Reachability

From **R1**, verify:
- `ping 10.0.0.2` and `ping 10.0.0.3` — IPv4 reachability to loopbacks
- `ping 2001:db8::2` and `ping 2001:db8::3` — IPv6 reachability to loopbacks
- Repeat from **R2** and **R3** to verify all directions

### Objective 5: Confirm K-Values Match

On all routers, verify that K-values are identical between address families:
- `show ip eigrp interfaces detail R1 Fa0/0` — note K1, K2, K3, K4, K5
- `show ipv6 eigrp interfaces detail R1 Fa0/0` — confirm same K-values

---

## 6. Verification & Analysis

### Step-by-step Verification Commands

**1. Verify IPv6 unicast routing is enabled:**
```
R1# show ipv6 interface brief
R1# show ipv6 route | include ::/0
```
Expected output: Link-local and site-local routes visible; no connected route if routing not enabled.

**2. Verify EIGRP named mode is active:**
```
R1# show ip eigrp neighbors
EIGRP-IPv4 Neighbors for AS(ENARSI)
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq Type
                                                   (sec)         (ms)   (ms)  Cnt Num
1   10.13.0.2               Fa1/0                    14 00:01:20  145   1200  0  2
0   10.12.0.2               Fa0/0                    11 00:00:58  156   1200  0  3
```
Notice: `AS(ENARSI)` — router eigrp ENARSI context, not `AS(100)`.

**3. Verify IPv6 address family has formed neighbors:**
```
R1# show ipv6 eigrp neighbors
EIGRP-IPv6 Neighbors for AS(ENARSI)
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq Type
                                                   (sec)         (ms)   (ms)  Cnt Num
1   FE80::2                 Fa1/0                    10 00:00:45  167   1200  0  1
0   FE80::3                 Fa0/0                    10 00:00:42  180   1200  0  2
```
Notice: Link-local addresses (FE80::x), not global unicast addresses.

**4. Verify IPv6 routes are in routing table:**
```
R1# show ipv6 route eigrp
IPv6 Routing Table - default - 10 entries
Codes: C - Connected, L - Local, S - Static, U - Per-user Static route
       B - BGP, EX - EIGRP external, O - OSPF, EI - OSPF inter, EA - OSPF external
       ND - ND Default, NDp - ND Prefix, DCE - Destination, NDr - Redirect
       O - OSPF, OI - OSPF inter, OE - OSPF external, ON1 - OSPF NSSA external type 1
       ON2 - OSPF NSSA external type 2, la - LISP alt, lr - LISP site-registrations
       ld - LISP dyn-EID, a - Application route
       D  - EIGRP, EX - EIGRP external

D   2001:db8::2/128 [90/1638400]
     via FE80::2, Fa0/0
D   2001:db8::3/128 [90/1638400]
     via FE80::3, Fa1/0
```

**5. Verify K-values are consistent:**
```
R1# show ip eigrp interfaces detail Fa0/0
EIGRP interfaces for process ID: ENARSI
                       Xmit Queue   PeerQ        Mean   Pacing Time   Multicast    Pending
Interface Peers  Un/Reliable  Un/Reliable  SRTT   Un/Reliable   Flow Timer   Routes
Fa0/0       2        0/0       0/0         118     0/0          329           0

Hello interval is 5 sec
Holdtime interval is 15 sec
Split horizon is enabled
Next xmit serial number is 6
Un-reliable mcasts: 0, Un-reliable ucasts: 1 Reliable mcasts/ucasts: 0/0
Mcast exceptions: 0, CR packets: 0, ACKs suppressed: 0
Retransmissions sent: 0, Out-of-sequence rcvs: 0
Authentication mode is not set
Topology-ids on interface - IPv4 : 0

K1 = 1, K2 = 0, K3 = 1, K4 = 0, K5 = 0
```

Repeat for IPv6 — K-values must be identical.

---

## 7. Verification Cheatsheet

**Quick wins to verify the lab is complete:**

```
# On all routers:
show eigrp neighbors                           # IPv4 peers in named mode
show ipv6 eigrp neighbors                      # IPv6 peers via link-local
show ip route eigrp                            # All learned IPv4 routes
show ipv6 route eigrp                          # All learned IPv6 routes
ping 10.0.0.X                                  # IPv4 reachability
ping 2001:db8::X                               # IPv6 reachability

# Specific troubleshooting:
show ip eigrp interfaces detail Fa0/0          # K-values, Hello, Hold
show ipv6 eigrp interfaces detail Fa0/0        # Confirm K-values match
debug eigrp packets                            # See hello/ACK exchanges
debug ipv6 eigrp packets                       # IPv6 packet capture
```

---

## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these configs first!

### Objective 1 Solution: Enable IPv6 Routing

<details>
<summary>Click to view Configuration</summary>

```
! R1, R2, R3
ipv6 unicast-routing
```

Verification:
```
show ipv6 route | include ^C
```

</details>

---

### Objective 2 Solution: Migrate R1 to Named Mode

<details>
<summary>Click to view R1 Configuration</summary>

```
R1# configure terminal
R1(config)# no router eigrp 100
R1(config)# router eigrp ENARSI
R1(config-router)# address-family ipv4 unicast autonomous-system 100
R1(config-router-af)# network 10.0.0.0 0.0.0.255
R1(config-router-af)# network 10.12.0.0 0.0.0.3
R1(config-router-af)# network 10.13.0.0 0.0.0.3
R1(config-router-af)# network 10.23.0.0 0.0.0.3
R1(config-router-af)# no auto-summary
R1(config-router-af)# exit-address-family
R1(config-router)# address-family ipv6 unicast autonomous-system 100
R1(config-router-af)# topology base
R1(config-router-af-topology)# exit-address-family
R1(config-router)# end
```

Note: For IPv6, network statements use the `topology base` context. Alternatively:
```
R1(config-router)# address-family ipv6 unicast autonomous-system 100
R1(config-router-af)# exit-address-family
! IPv6 networks are derived from interface configurations with 'ipv6 eigrp X' commands on each interface
```

</details>

<details>
<summary>Click to view R1 Interface Configuration (IPv6)</summary>

```
R1# configure terminal
R1(config)# interface Fa0/0
R1(config-if)# ipv6 eigrp ENARSI
R1(config-if)# exit
R1(config)# interface Fa1/0
R1(config-if)# ipv6 eigrp ENARSI
R1(config-if)# exit
R1(config)# interface Lo0
R1(config-if)# ipv6 eigrp ENARSI
R1(config-if)# end
```

Note: IPv6 EIGRP participation is enabled on a per-interface basis, not via network statements.

</details>

---

### Objective 3 Solution: Migrate R2 and R3

<details>
<summary>Click to view R2 and R3 Migration (same pattern as R1)</summary>

```
! R2
ipv6 unicast-routing
no router eigrp 100
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  network 10.0.0.0 0.0.0.255
  network 10.12.0.0 0.0.0.3
  network 10.13.0.0 0.0.0.3
  network 10.23.0.0 0.0.0.3
  no auto-summary
  exit-address-family
 address-family ipv6 unicast autonomous-system 100
  exit-address-family
!
interface Fa0/0
 ipv6 eigrp ENARSI
interface Fa0/1
 ipv6 eigrp ENARSI
interface Lo0
 ipv6 eigrp ENARSI

! R3 (identical pattern)
```

</details>

---

### Objective 4 Solution: Verify Reachability

<details>
<summary>Click to view Verification Commands</summary>

```
R1# ping 10.0.0.2
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 10.0.0.2, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), roundtrip min/avg/max = 1/1/4 ms

R1# ping 2001:db8::2
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 2001:db8::2, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), roundtrip min/avg/max = 1/2/5 ms

! Repeat for 10.0.0.3 and 2001:db8::3
```

</details>

---

### Objective 5 Solution: Confirm K-Values

<details>
<summary>Click to view K-Value Verification</summary>

```
R1# show ip eigrp interfaces detail Fa0/0 | include "^K"
K1 = 1, K2 = 0, K3 = 1, K4 = 0, K5 = 0

R1# show ipv6 eigrp interfaces detail Fa0/0 | include "^K"
K1 = 1, K2 = 0, K3 = 1, K4 = 0, K5 = 0
```

If K-values differ between address families, neighbors will NOT form. This is a silent failure — debug with:
```
R1# debug eigrp packet hello
```

</details>

---

## 9. Troubleshooting Scenarios

Each ticket simulates a real-world fault. Inject the fault first, then diagnose and fix using only show commands.

### Workflow

```bash
python3 setup_lab.py                                   # reset to known-good
python3 scripts/fault-injection/inject_scenario_01.py  # Ticket 1
python3 scripts/fault-injection/apply_solution.py      # restore
```

---

### Ticket 1 — IPv6 Loopback Addresses Missing from Routing Table

You migrate R1 to named mode with IPv6 EIGRP, but `show ipv6 route eigrp` on R2 and R3 does not show R1's loopback address.

**Inject:** `python3 scripts/fault-injection/inject_scenario_01.py`

**Success criteria:** After fix, `show ipv6 route eigrp` on R2 shows `2001:db8::1/128 via FE80::1`.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. Verify IPv6 routing is enabled globally:
   ```
   show ipv6 cef summary
   ```

2. Check if R1's loopback is participating in IPv6 EIGRP:
   ```
   show ipv6 eigrp interfaces | include Loopback
   ! Expected: Loopback0 listed for EIGRP process
   ```

3. Verify the loopback has an IPv6 address:
   ```
   show ipv6 interface Lo0 | include "inet6"
   ! Expected: 2001:db8::1/128
   ```

4. Check if R1 is advertising the loopback in EIGRP:
   ```
   show ipv6 eigrp topology 2001:db8::1/128
   ! If empty: not being advertised
   ```

**Root cause:** Loopback0 is not configured with the IPv6 EIGRP process. The interface has an IPv6 address but is not participating in the address family.

</details>

<details>
<summary>Click to view Fix</summary>

On **R1**, add the loopback interface to IPv6 EIGRP:

```
R1# configure terminal
R1(config)# interface Lo0
R1(config-if)# ipv6 eigrp ENARSI
R1(config-if)# end
```

Verify:
```
R1# show ipv6 eigrp topology 2001:db8::1/128
```

Then check R2 and R3:
```
R2# show ipv6 route eigrp | include 2001:db8::1
D   2001:db8::1/128 [90/...] via FE80::1, Fa0/0
```

</details>

---

### Ticket 2 — IPv6 Neighbors Not Forming After Named Mode Migration

After migrating all three routers to named mode, `show ipv6 eigrp neighbors` is empty on all routers, but `show ip eigrp neighbors` still shows peers.

**Inject:** `python3 scripts/fault-injection/inject_scenario_02.py`

**Success criteria:** `show ipv6 eigrp neighbors` shows active neighbors with link-local addresses on all three routers.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. Verify the named-mode EIGRP instance is active:
   ```
   show eigrp plugins
   ! Check for ENARSI instance
   ```

2. Verify IPv6 unicast routing is enabled:
   ```
   show ipv6 cef summary
   ! If CEFv6 is not enabled, IPv6 routing is disabled
   ```

3. Check interface configuration:
   ```
   show ipv6 interface Fa0/0 | include "link-local"
   ! Expected: FE80::X link-local address present
   ```

4. Verify EIGRP is running on the interface:
   ```
   show ipv6 eigrp interfaces Fa0/0
   ! If empty or no EIGRP output: address family not enabled on interface
   ```

5. Check for multicast routing:
   ```
   show ipv6 route
   ! Look for ff02::a entry (EIGRP multicast destination)
   ```

**Root cause:** Most likely — IPv6 unicast routing is not enabled, OR the interface does not have the IPv6 EIGRP command applied.

</details>

<details>
<summary>Click to view Fix</summary>

**On all three routers:**

```
R1# configure terminal

! 1. Enable IPv6 unicast routing (if not already done)
R1(config)# ipv6 unicast-routing

! 2. Verify each interface has IPv6 EIGRP enabled
R1(config)# interface Fa0/0
R1(config-if)# ipv6 eigrp ENARSI
R1(config-if)# exit

R1(config)# interface Fa1/0
R1(config-if)# ipv6 eigrp ENARSI
R1(config-if)# exit

R1(config)# interface Lo0
R1(config-if)# ipv6 eigrp ENARSI
R1(config-if)# end
```

**Repeat for R2 and R3** (using their respective interface names).

Verify:
```
R1# show ipv6 eigrp neighbors
```

</details>

---

### Ticket 3 — K-Value Mismatch Between IPv4 and IPv6 Address Families

On R1, `show ip eigrp interfaces detail` and `show ipv6 eigrp interfaces detail` show different K-values. Neighbors form for IPv4 but fail to form for IPv6.

**Inject:** `python3 scripts/fault-injection/inject_scenario_03.py`

**Success criteria:** K-values are identical across both address families. IPv6 neighbors form.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. Check IPv4 K-values:
   ```
   R1# show ip eigrp interfaces detail Fa0/0 | include "^K"
   K1 = 1, K2 = 0, K3 = 1, K4 = 0, K5 = 0
   ```

2. Check IPv6 K-values:
   ```
   R1# show ipv6 eigrp interfaces detail Fa0/0 | include "^K"
   K1 = 1, K2 = 0, K3 = 1, K4 = 0, K5 = 0
   ```

3. If they differ, check the EIGRP process configuration:
   ```
   R1# show running-config | section "router eigrp"
   ! Look for explicit metric weights commands under each address family
   ```

**Root cause:** The IPv6 address family has explicit `metric weights` command configured differently from the IPv4 address family. EIGRP requires all neighbors in all address families to have identical K-values.

</details>

<details>
<summary>Click to view Fix</summary>

On **R1**, ensure both address families use default K-values:

```
R1# configure terminal
R1(config)# router eigrp ENARSI
R1(config-router)# address-family ipv6 unicast autonomous-system 100
R1(config-router-af)# no metric weights
R1(config-router-af)# exit-address-family
R1(config-router)# end
```

If you previously configured custom K-values, remove them:
```
no metric weights 0 1 0 1 0 0 0
```

Verify:
```
R1# show ipv6 eigrp interfaces detail Fa0/0 | include "^K"
! Should now match IPv4 K-values
```

</details>

---

### Ticket 4 — Named Mode Not Active; Classic Mode Still Running

On R1, `show run | section eigrp` shows `router eigrp 100` instead of `router eigrp ENARSI`. IPv4 neighbors are connected but the migration is incomplete.

**Inject:** `python3 scripts/fault-injection/inject_scenario_04.py`

**Success criteria:** `show ip eigrp neighbors` displays `AS(ENARSI)` not `AS(100)`.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. Check current EIGRP configuration:
   ```
   R1# show running-config | section "router eigrp"
   router eigrp 100
    network 10.0.0.0 0.0.0.255
    ...
   ! Classic mode active
   ```

2. Check active processes:
   ```
   R1# show ip eigrp neighbors
   EIGRP-IPv4 Neighbors for AS(100)
   ! Shows AS(100), not AS(ENARSI)
   ```

**Root cause:** The `no router eigrp 100` command was not issued before configuring the named-mode router. Both instances are running in parallel, or the named mode configuration was not applied.

</details>

<details>
<summary>Click to view Fix</summary>

**On R1:**

```
R1# configure terminal

! 1. Stop the classic mode instance
R1(config)# no router eigrp 100

! 2. Configure named mode (if not already present)
R1(config)# router eigrp ENARSI
R1(config-router)# address-family ipv4 unicast autonomous-system 100
R1(config-router-af)# network 10.0.0.0 0.0.0.255
R1(config-router-af)# network 10.12.0.0 0.0.0.3
R1(config-router-af)# network 10.13.0.0 0.0.0.3
R1(config-router-af)# network 10.23.0.0 0.0.0.3
R1(config-router-af)# no auto-summary
R1(config-router-af)# exit-address-family
R1(config-router)# address-family ipv6 unicast autonomous-system 100
R1(config-router-af)# exit-address-family
R1(config-router)# end
```

Verify:
```
R1# show ip eigrp neighbors
EIGRP-IPv4 Neighbors for AS(ENARSI)
```

</details>

---

### Ticket 5 — Passive Interface Configured on IPv4 but Not IPv6

On R2, `show ip eigrp interfaces` shows Fa0/0 as normal, but `show ipv6 eigrp interfaces` shows Fa0/0 as passive. IPv4 neighbors form but IPv6 does not.

**Inject:** `python3 scripts/fault-injection/inject_scenario_05.py`

**Success criteria:** Both `show ip eigrp interfaces` and `show ipv6 eigrp interfaces` show Fa0/0 as active (not passive).

<details>
<summary>Click to view Diagnosis Steps</summary>

1. Check IPv4 interface state:
   ```
   R2# show ip eigrp interfaces Fa0/0 | include "Peers\|Hello\|Passive"
   ```

2. Check IPv6 interface state:
   ```
   R2# show ipv6 eigrp interfaces Fa0/0 | include "Peers\|Hello\|Passive"
   ! If it says "Passive: Yes", the interface is not sending EIGRP packets
   ```

3. Check the configuration:
   ```
   R2# show running-config | include "passive-interface"
   ```

**Root cause:** A passive-interface command was applied in one address family but not mirrored in the other. Or a blanket `passive-interface default` was issued and specific address families were not enabled.

</details>

<details>
<summary>Click to view Fix</summary>

**On R2:**

```
R2# configure terminal
R2(config)# router eigrp ENARSI

! For IPv4 address family
R2(config-router)# address-family ipv4 unicast autonomous-system 100
R2(config-router-af)# no passive-interface Fa0/0
R2(config-router-af)# exit-address-family

! For IPv6 address family
R2(config-router)# address-family ipv6 unicast autonomous-system 100
R2(config-router-af)# no passive-interface Fa0/0
R2(config-router-af)# exit-address-family

R2(config-router)# end
```

Verify:
```
R2# show ipv6 eigrp interfaces Fa0/0 | include "Passive"
! Should show: Passive: No
```

</details>

---

## 10. Lab Completion Checklist

### Core Implementation

- [ ] IPv6 unicast routing enabled on all routers
- [ ] All routers migrated from classic mode (`router eigrp 100`) to named mode (`router eigrp ENARSI`)
- [ ] IPv4 address family configured with AS 100 on all routers
- [ ] IPv6 address family configured with AS 100 on all routers
- [ ] All interfaces (Fa0/0, Fa0/1, Fa0/1 for R2/R3, Lo0) have IPv6 EIGRP enabled
- [ ] IPv4 neighbor adjacencies stable (`show ip eigrp neighbors` shows 2 peers per router)
- [ ] IPv6 neighbor adjacencies stable (`show ipv6 eigrp neighbors` shows 2 peers per router)
- [ ] All IPv4 loopbacks reachable from all routers (`ping 10.0.0.X`)
- [ ] All IPv6 loopbacks reachable from all routers (`ping 2001:db8::X`)
- [ ] K-values identical between IPv4 and IPv6 address families on all interfaces

### Troubleshooting Scenarios

- [ ] Ticket 1 — IPv6 loopback not advertised: diagnosed and fixed
- [ ] Ticket 2 — IPv6 neighbors not forming: diagnosed and fixed
- [ ] Ticket 3 — K-value mismatch: diagnosed and fixed
- [ ] Ticket 4 — Classic mode still active: diagnosed and fixed
- [ ] Ticket 5 — Passive interface on one AF only: diagnosed and fixed

**Lab Complete!** Both IPv4 and IPv6 address families are stable, neighbors are active, and you've practiced troubleshooting dual-stack EIGRP deployments.
