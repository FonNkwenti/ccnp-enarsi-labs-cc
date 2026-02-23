# EIGRP Lab 02: Dual-Stack EIGRP — IPv4 & IPv6 Classic Mode

## 1. Concepts & Skills Covered

**Exam Bullets:**
- 1.9.a Address families (IPv4, IPv6)
- 1.9.b Neighbor adjacency

**What You'll Learn:**
- How to configure IPv6 EIGRP in classic IOS mode using `ipv6 router eigrp` and per-interface `ipv6 eigrp` commands
- How IPv4 (`router eigrp 100`) and IPv6 (`ipv6 router eigrp 100`) run as independent processes on the same router
- How to verify both IPv4 and IPv6 neighbor adjacencies and routing tables
- Why K-values must match between all EIGRP neighbors (IPv4 and IPv6 processes share the same K-values on classic IOS)
- Troubleshooting IPv6 unicast routing and classic-mode IPv6 EIGRP misconfigurations

**Key Concepts:**
- **Independent Processes**: IPv4 EIGRP (`router eigrp 100`) and IPv6 EIGRP (`ipv6 router eigrp 100`) are completely separate processes in classic IOS mode — each has its own neighbor table, topology table, and routing table
- **Address Family Context**: IPv4 uses `network` statements under `router eigrp 100`; IPv6 uses per-interface `ipv6 eigrp 100` commands — no `network` statements are needed for IPv6
- **K-Values**: Must match between all EIGRP-speaking neighbors; default is K1=1, K3=1, K2=0, K4=0, K5=0
- **IPv6 Routing**: Requires `ipv6 unicast-routing` globally; EIGRP uses link-local addresses for hellos

---

## 2. Topology & Scenario

**Enterprise Context:**
Acme Corp has a working IPv4-only EIGRP classic mode network (Lab 01 state). The operations team is now adding IPv6 support across the WAN to prepare for a dual-stack deployment. The IPv4 EIGRP process must remain unaffected while IPv6 EIGRP is brought up alongside it.

You are the network engineer tasked with:
1. Enabling IPv6 unicast routing globally on all three routers
2. Configuring the IPv6 EIGRP classic mode process (`ipv6 router eigrp 100`) on each router
3. Enabling IPv6 EIGRP participation on each relevant interface
4. Verifying that both IPv4 and IPv6 neighbors form adjacencies

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

All three routers are running **EIGRP classic mode (AS 100)** with IPv4 adjacencies already formed and stable. IPv6 addresses are pre-configured on all interfaces and loopbacks, but IPv6 EIGRP is NOT yet configured.

```
R1, R2, R3 — already configured:
- router eigrp 100
- network 10.0.0.0 0.0.0.255
- network 10.12.0.0 0.0.0.3  (R1, R2)
- network 10.13.0.0 0.0.0.3  (R1, R3)
- network 10.23.0.0 0.0.0.3  (R2, R3)
- no auto-summary
- IPv6 addresses on all interfaces (pre-configured)
- IPv6 EIGRP NOT configured
```

**Your Task in This Lab:**

Configure the IPv6 EIGRP classic mode process on all routers and enable per-interface participation:

1. Enable `ipv6 unicast-routing` globally
2. Configure `ipv6 router eigrp 100` with `no shutdown`
3. Apply `ipv6 eigrp 100` on each interface that should participate

---

## 5. Lab Challenge: Core Implementation

You have one maintenance window to add IPv6 EIGRP to the existing IPv4-only network. The IPv4 classic configuration must remain unaffected throughout.

### Objective 1: Enable IPv6 Routing

On **all three routers**, enable IPv6 unicast routing globally.

**Verification:** `show ipv6 route` shows local IPv6 routes (not empty).

### Objective 2: Configure the IPv6 EIGRP Process

On **each router**, configure the IPv6 EIGRP classic mode process. The process number must match the IPv4 AS number (100).

```
ipv6 router eigrp 100
 no shutdown
```

Note: The `no shutdown` command is required — the IPv6 EIGRP process starts in a shutdown state by default.

**Verification (R1):**
- `show ipv6 eigrp neighbors` — should be empty until interfaces are enabled (Objective 3)

### Objective 3: Enable IPv6 EIGRP Per-Interface

On **each router**, enable IPv6 EIGRP participation on every interface that should be included. This replaces the `network` statement used in IPv4 — there are no `network` statements in classic IPv6 EIGRP.

Apply `ipv6 eigrp 100` to: Lo0, Fa0/0, Fa1/0 (R1), Fa0/0 and Fa0/1 (R2 and R3).

**Verification after all interfaces are enabled:**
- `show ipv6 eigrp neighbors` — shows R2 and R3 (from R1), using link-local addresses
- `show ipv6 eigrp interfaces` — lists all participating interfaces

### Objective 4: Verify Dual-Stack Reachability

From **R1**, verify both stacks are fully functional:
- `ping 10.0.0.2` and `ping 10.0.0.3` — IPv4 loopback reachability
- `ping 2001:db8::2` and `ping 2001:db8::3` — IPv6 loopback reachability

Repeat from **R2** and **R3** to confirm all directions.

### Objective 5: Confirm K-Values Match

On all routers, verify that K-values are identical between the IPv4 and IPv6 EIGRP processes:
- `show ip eigrp interfaces detail Fa0/0` — note K1, K2, K3, K4, K5
- `show ipv6 eigrp interfaces detail Fa0/0` — confirm same K-values

---

## 6. Verification & Analysis

### Step-by-step Verification Commands

**1. Verify IPv6 unicast routing is enabled:**
```
R1# show ipv6 interface brief
```
Expected: All interfaces with IPv6 addresses show link-local and global addresses.

**2. Verify IPv6 EIGRP process is active:**
```
R1# show ipv6 protocols
```
Expected output includes the IPv6 EIGRP process:
```
IPv6 Routing Protocol is "eigrp 100"
  EIGRP-IPv6 Protocol for AS(100)
  ...
  Interfaces:
    Loopback0
    FastEthernet0/0
    FastEthernet1/0
```

**3. Verify IPv6 EIGRP neighbors have formed:**
```
R1# show ipv6 eigrp neighbors
EIGRP-IPv6 Neighbors for AS(100)
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq Type
                                                   (sec)         (ms)   (ms)  Cnt Num
1   Link-local address      Fa1/0                    10 00:00:45  167   1200  0  1
0   Link-local address      Fa0/0                    10 00:00:42  180   1200  0  2
```
Note: Neighbors are identified by link-local addresses (FE80::x), not global unicast.

**4. Verify IPv6 routes are in routing table:**
```
R1# show ipv6 route eigrp
```
Expected:
```
D   2001:db8::2/128 [90/1638400]
     via FE80::X, FastEthernet0/0
D   2001:db8::3/128 [90/1638400]
     via FE80::X, FastEthernet1/0
```

**5. Verify K-values are consistent:**
```
R1# show ip eigrp interfaces detail Fa0/0 | include K
K1 = 1, K2 = 0, K3 = 1, K4 = 0, K5 = 0

R1# show ipv6 eigrp interfaces detail Fa0/0 | include K
K1 = 1, K2 = 0, K3 = 1, K4 = 0, K5 = 0
```
Both must be identical. A mismatch prevents IPv6 neighbor formation.

---

## 7. Verification Cheatsheet

**Quick wins to verify the lab is complete:**

```
# On all routers:
show ipv6 protocols                            # Confirm IPv6 EIGRP process 100 active
show ipv6 eigrp neighbors                      # IPv6 peers via link-local addresses
show ip eigrp neighbors                        # IPv4 peers still healthy (AS 100)
show ip route eigrp                            # All learned IPv4 routes
show ipv6 route eigrp                          # All learned IPv6 routes
ping 10.0.0.X                                  # IPv4 loopback reachability
ping 2001:db8::X                               # IPv6 loopback reachability

# Specific troubleshooting:
show ipv6 eigrp interfaces                     # List interfaces in IPv6 EIGRP
show ip eigrp interfaces detail Fa0/0          # K-values, Hello, Hold (IPv4)
show ipv6 eigrp interfaces detail Fa0/0        # K-values, Hello, Hold (IPv6)
debug ipv6 eigrp packets                       # IPv6 EIGRP packet capture
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
Connected IPv6 routes should appear.

</details>

---

### Objective 2 Solution: Configure the IPv6 EIGRP Process

<details>
<summary>Click to view Configuration</summary>

```
! R1, R2, R3
ipv6 router eigrp 100
 no shutdown
```

The `no shutdown` is required. Without it, the process is administratively down and no neighbors will form.

</details>

---

### Objective 3 Solution: Enable IPv6 EIGRP Per-Interface

<details>
<summary>Click to view R1 Configuration</summary>

```
! R1
interface Lo0
 ipv6 eigrp 100
!
interface Fa0/0
 ipv6 eigrp 100
!
interface Fa1/0
 ipv6 eigrp 100
```

</details>

<details>
<summary>Click to view R2 Configuration</summary>

```
! R2
interface Lo0
 ipv6 eigrp 100
!
interface Fa0/0
 ipv6 eigrp 100
!
interface Fa0/1
 ipv6 eigrp 100
```

</details>

<details>
<summary>Click to view R3 Configuration</summary>

```
! R3
interface Lo0
 ipv6 eigrp 100
!
interface Fa0/0
 ipv6 eigrp 100
!
interface Fa0/1
 ipv6 eigrp 100
```

</details>

---

### Complete Solution: All Routers

<details>
<summary>Click to view complete dual-stack configuration for all routers</summary>

```
! ============================
! R1
! ============================
ipv6 unicast-routing
!
interface Lo0
 ipv6 address 2001:db8::1/128
 ipv6 eigrp 100
!
interface Fa0/0
 ipv6 address 2001:db8:12::1/64
 ipv6 eigrp 100
!
interface Fa1/0
 ipv6 address 2001:db8:13::1/64
 ipv6 eigrp 100
!
ipv6 router eigrp 100
 no shutdown

! ============================
! R2
! ============================
ipv6 unicast-routing
!
interface Lo0
 ipv6 address 2001:db8::2/128
 ipv6 eigrp 100
!
interface Fa0/0
 ipv6 address 2001:db8:12::2/64
 ipv6 eigrp 100
!
interface Fa0/1
 ipv6 address 2001:db8:23::1/64
 ipv6 eigrp 100
!
ipv6 router eigrp 100
 no shutdown

! ============================
! R3
! ============================
ipv6 unicast-routing
!
interface Lo0
 ipv6 address 2001:db8::3/128
 ipv6 eigrp 100
!
interface Fa0/0
 ipv6 address 2001:db8:13::2/64
 ipv6 eigrp 100
!
interface Fa0/1
 ipv6 address 2001:db8:23::2/64
 ipv6 eigrp 100
!
ipv6 router eigrp 100
 no shutdown
```

No `router eigrp ENARSI`, no `address-family` blocks. IPv4 EIGRP (`router eigrp 100`) remains unchanged from Lab 01.

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
R1# show ip eigrp interfaces detail Fa0/0 | include K
K1 = 1, K2 = 0, K3 = 1, K4 = 0, K5 = 0

R1# show ipv6 eigrp interfaces detail Fa0/0 | include K
K1 = 1, K2 = 0, K3 = 1, K4 = 0, K5 = 0
```

If K-values differ between processes, neighbors will NOT form. This is a silent failure — diagnose with:
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

### Ticket 1 — IPv6 Loopback Not Advertised into EIGRP

R2 and R3 run `show ipv6 route eigrp` and R1's loopback `2001:db8::1/128` does not appear. IPv4 routing is normal.

**Inject:** `python3 scripts/fault-injection/inject_scenario_01.py`

**Success criteria:** After fix, `show ipv6 route eigrp` on R2 shows `2001:db8::1/128 via FE80::1`.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. Verify IPv6 routing is enabled globally on R1:
   ```
   R1# show ipv6 cef summary
   ```

2. Check which interfaces are participating in IPv6 EIGRP on R1:
   ```
   R1# show ipv6 eigrp interfaces
   ! Is Loopback0 listed?
   ```

3. Verify the loopback has an IPv6 address:
   ```
   R1# show ipv6 interface Lo0 | include Global
   ! Expected: 2001:db8::1/128
   ```

4. Check if R1 is advertising the loopback in the topology:
   ```
   R1# show ipv6 eigrp topology 2001:db8::1/128
   ! If empty: not being advertised
   ```

**Root cause:** Loopback0 does not have `ipv6 eigrp 100` configured. The interface has an IPv6 address but is not participating in the IPv6 EIGRP process.

</details>

<details>
<summary>Click to view Fix</summary>

On **R1**, add the loopback interface to the IPv6 EIGRP process:

```
R1# configure terminal
R1(config)# interface Lo0
R1(config-if)# ipv6 eigrp 100
R1(config-if)# end
```

Verify:
```
R1# show ipv6 eigrp interfaces | include Loop
R2# show ipv6 route eigrp | include 2001:db8::1
D   2001:db8::1/128 [90/...] via FE80::1, Fa0/0
```

</details>

---

### Ticket 2 — IPv6 Neighbors Not Forming on Any Router

After the IPv6 EIGRP process is configured on all three routers, `show ipv6 eigrp neighbors` is empty everywhere. IPv4 neighbors are stable.

**Inject:** `python3 scripts/fault-injection/inject_scenario_02.py`

**Success criteria:** `show ipv6 eigrp neighbors` shows active neighbors with link-local addresses on all three routers.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. Verify IPv6 unicast routing is enabled:
   ```
   R1# show ipv6 cef summary
   ! If CEFv6 is not running, IPv6 routing is disabled globally
   ```

2. Check if the IPv6 EIGRP process is up (not shutdown):
   ```
   R1# show ipv6 protocols
   ! Look for "EIGRP-IPv6 Protocol for AS(100)"
   ! If absent or shows "shutdown", the process needs no shutdown
   ```

3. Check interface participation:
   ```
   R1# show ipv6 eigrp interfaces
   ! If this list is empty, no interfaces have ipv6 eigrp 100 configured
   ```

4. Verify link-local addresses are present:
   ```
   R1# show ipv6 interface Fa0/0 | include "link-local"
   ! Expected: FE80::X link-local address
   ```

**Root cause:** Most likely — `ipv6 unicast-routing` is missing, OR the `ipv6 router eigrp 100` process was not brought up with `no shutdown`.

</details>

<details>
<summary>Click to view Fix</summary>

**On all three routers:**

```
! 1. Enable IPv6 unicast routing
R1(config)# ipv6 unicast-routing

! 2. Ensure the process is not shutdown
R1(config)# ipv6 router eigrp 100
R1(config-rtr)# no shutdown
R1(config-rtr)# exit

! 3. Verify each interface has IPv6 EIGRP enabled
R1(config)# interface Fa0/0
R1(config-if)# ipv6 eigrp 100
R1(config-if)# exit

R1(config)# interface Fa1/0
R1(config-if)# ipv6 eigrp 100
R1(config-if)# exit

R1(config)# interface Lo0
R1(config-if)# ipv6 eigrp 100
R1(config-if)# end
```

Repeat for R2 and R3 with their respective interfaces.

Verify:
```
R1# show ipv6 eigrp neighbors
```

</details>

---

### Ticket 3 — K-Value Mismatch Prevents IPv6 Neighbor Formation

On R1, `show ip eigrp interfaces detail` and `show ipv6 eigrp interfaces detail` show different K-values. IPv4 neighbors form normally; IPv6 neighbors will not form with R1.

**Inject:** `python3 scripts/fault-injection/inject_scenario_03.py`

**Success criteria:** K-values are identical between the IPv4 and IPv6 processes on all routers. IPv6 neighbors form.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. Check IPv4 EIGRP K-values:
   ```
   R1# show ip eigrp interfaces detail Fa0/0 | include K
   K1 = 1, K2 = 0, K3 = 1, K4 = 0, K5 = 0
   ```

2. Check IPv6 EIGRP K-values:
   ```
   R1# show ipv6 eigrp interfaces detail Fa0/0 | include K
   K1 = 1, K2 = 1, K3 = 1, K4 = 0, K5 = 0
   ! K2 = 1 differs from IPv4 (K2 = 0)
   ```

3. Check the running configuration:
   ```
   R1# show running-config | section "ipv6 router eigrp"
   ! Look for explicit metric weights command
   ```

**Root cause:** An explicit `metric weights` command was applied under `ipv6 router eigrp 100` that differs from the IPv4 default K-values. EIGRP requires matching K-values for neighbor formation.

</details>

<details>
<summary>Click to view Fix</summary>

On **R1**, restore default K-values under the IPv6 EIGRP process:

```
R1# configure terminal
R1(config)# ipv6 router eigrp 100
R1(config-rtr)# no metric weights
R1(config-rtr)# end
```

Verify:
```
R1# show ipv6 eigrp interfaces detail Fa0/0 | include K
! Should now show K1 = 1, K2 = 0, K3 = 1, K4 = 0, K5 = 0
```

</details>

---

### Ticket 4 — IPv6 EIGRP Process Removed from R1

`show ipv6 eigrp neighbors` on R2 and R3 is empty for entries pointing to R1. IPv4 neighbors with R1 are normal. R2 has no route to `2001:db8::1/128`.

**Inject:** `python3 scripts/fault-injection/inject_scenario_04.py`

**Success criteria:** R1 shows IPv6 EIGRP neighbors for R2 and R3. R2 and R3 have `2001:db8::1/128` in `show ipv6 route eigrp`.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. Check if the IPv6 EIGRP process exists on R1:
   ```
   R1# show ipv6 protocols
   ! If the EIGRP-IPv6 process for AS(100) is absent, the process was removed
   ```

2. Verify via running config:
   ```
   R1# show run | include "ipv6 router eigrp"
   ! Empty output confirms the process is gone
   ```

3. Check interface config — per-interface commands may also be gone:
   ```
   R1# show run interface Lo0 | include "ipv6 eigrp"
   R1# show run interface Fa0/0 | include "ipv6 eigrp"
   ```

**Root cause:** `no ipv6 router eigrp 100` was issued on R1, removing the process and all associated interface-level `ipv6 eigrp 100` commands.

</details>

<details>
<summary>Click to view Fix</summary>

On **R1**, recreate the IPv6 EIGRP process and re-enable all interfaces:

```
R1# configure terminal
R1(config)# ipv6 router eigrp 100
R1(config-rtr)# no shutdown
R1(config-rtr)# exit
!
R1(config)# interface Lo0
R1(config-if)# ipv6 eigrp 100
R1(config-if)# exit
!
R1(config)# interface Fa0/0
R1(config-if)# ipv6 eigrp 100
R1(config-if)# exit
!
R1(config)# interface Fa1/0
R1(config-if)# ipv6 eigrp 100
R1(config-if)# end
```

Verify:
```
R1# show ipv6 eigrp neighbors
R2# show ipv6 route eigrp | include 2001:db8::1
```

</details>

---

### Ticket 5 — Passive Interface Blocks IPv6 EIGRP on R2 Fa0/0

On R2, `show ip eigrp interfaces` lists Fa0/0 as active, but `show ipv6 eigrp interfaces` does not list Fa0/0 (or lists it as passive). IPv4 neighbors form normally; R1 has no IPv6 neighbor relationship with R2.

**Inject:** `python3 scripts/fault-injection/inject_scenario_05.py`

**Success criteria:** Both `show ip eigrp interfaces` and `show ipv6 eigrp interfaces` show Fa0/0 as active on R2. R1 shows R2 as an IPv6 EIGRP neighbor.

<details>
<summary>Click to view Diagnosis Steps</summary>

1. Check IPv6 EIGRP interface list on R2:
   ```
   R2# show ipv6 eigrp interfaces
   ! If Fa0/0 is absent or shows Passive, it is not sending hellos
   ```

2. Check the IPv6 EIGRP process configuration:
   ```
   R2# show run | section "ipv6 router eigrp"
   ! Look for: passive-interface FastEthernet0/0
   ```

3. Compare IPv4 and IPv6 interface states:
   ```
   R2# show ip eigrp interfaces Fa0/0
   R2# show ipv6 eigrp interfaces Fa0/0
   ```

**Root cause:** `passive-interface FastEthernet0/0` was configured under `ipv6 router eigrp 100` but not under `router eigrp 100`, causing a split between the two processes.

</details>

<details>
<summary>Click to view Fix</summary>

**On R2:**

```
R2# configure terminal
R2(config)# ipv6 router eigrp 100
R2(config-rtr)# no passive-interface FastEthernet0/0
R2(config-rtr)# end
```

Verify:
```
R2# show ipv6 eigrp interfaces | include Fa0/0
R1# show ipv6 eigrp neighbors
! R2 should now appear as a neighbor
```

</details>

---

## 10. Lab Completion Checklist

### Core Implementation

- [ ] IPv6 unicast routing enabled on all routers
- [ ] IPv6 EIGRP process (`ipv6 router eigrp 100`) configured on all routers
- [ ] `no shutdown` issued under `ipv6 router eigrp 100` on all routers
- [ ] All relevant interfaces have `ipv6 eigrp 100` configured (Lo0, Fa0/0, Fa1/0 on R1; Lo0, Fa0/0, Fa0/1 on R2 and R3)
- [ ] IPv4 neighbor adjacencies stable (`show ip eigrp neighbors` shows 2 peers per router)
- [ ] IPv6 neighbor adjacencies stable (`show ipv6 eigrp neighbors` shows 2 peers per router)
- [ ] All IPv4 loopbacks reachable from all routers (`ping 10.0.0.X`)
- [ ] All IPv6 loopbacks reachable from all routers (`ping 2001:db8::X`)
- [ ] K-values identical between IPv4 and IPv6 processes on all interfaces

### Troubleshooting Scenarios

- [ ] Ticket 1 — IPv6 loopback not advertised: diagnosed and fixed
- [ ] Ticket 2 — IPv6 neighbors not forming: diagnosed and fixed
- [ ] Ticket 3 — K-value mismatch: diagnosed and fixed
- [ ] Ticket 4 — IPv6 EIGRP process removed from R1: diagnosed and fixed
- [ ] Ticket 5 — Passive interface on IPv6 process only: diagnosed and fixed

**Lab Complete!** Both IPv4 and IPv6 EIGRP processes are stable, all neighbors are active, and you have practiced troubleshooting classic-mode dual-stack EIGRP deployments.
