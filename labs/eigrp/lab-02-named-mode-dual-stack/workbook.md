# Lab 02 — EIGRP Named Mode & Dual-Stack IPv6 Address Family

**Chapter:** EIGRP | **Exam:** 300-410 ENARSI | **Blueprint:** 1.9.a, 1.9.b
**Difficulty:** Foundation | **Estimated Time:** 75 minutes

---

## Section 1 — Concepts & Skills Covered

**Exam Objective:** CCNP ENARSI 1.9.a, 1.9.b — Named Mode & Dual-Stack IPv6

Named mode EIGRP is the Cisco-recommended configuration model and the format the ENARSI exam tests. This lab transitions from the classic single-process model introduced in Lab 01 to the hierarchical named mode structure, then extends it with a full IPv6 address family. Understanding how the two address families are activated, why the IPv6 AF requires an explicit router-id, and what happens during a classic-to-named migration are all exam-tested concepts.

### Named Mode EIGRP

Named mode EIGRP (introduced in IOS 15.0) replaces the classic single-process model with a hierarchical structure that supports multiple address families under one named process. The process is identified by a name rather than an AS number:

```
router eigrp <NAME>
 address-family ipv4 unicast autonomous-system <AS>
  ...
 exit-address-family
 address-family ipv6 unicast autonomous-system <AS>
  ...
 exit-address-family
```

Named mode is the Cisco-recommended configuration model for all modern EIGRP deployments and is the format tested on the ENARSI exam.

### Address Families

Each address family (AF) operates independently within the named process:

| Address Family | Command | Network Statements | Router ID |
|----------------|---------|-------------------|-----------|
| IPv4 unicast | `address-family ipv4 unicast autonomous-system <AS>` | Required (`network` command) | Optional but recommended |
| IPv6 unicast | `address-family ipv6 unicast autonomous-system <AS>` | Not used — activates on all IPv6 interfaces | **Mandatory** (must be IPv4 format) |

### IPv6 EIGRP Prerequisites

Before the IPv6 address family can form adjacencies:
1. **`ipv6 unicast-routing`** must be enabled globally on every router
2. **IPv6 addresses** must be configured on all participating interfaces
3. **`eigrp router-id`** must be set explicitly in the IPv6 AF — EIGRP router IDs are always expressed as 32-bit IPv4 dotted-decimal values

### Migration: Classic → Named Mode

Classic and named mode **cannot coexist** for the same AS on the same router. The migration sequence is:
1. Note the existing network statements
2. Remove the classic process: `no router eigrp <AS>`
3. Configure the named process with the IPv4 AF, replicating the network statements
4. Add the IPv6 AF

There is a brief convergence event during migration — adjacencies reset and reform under the new process.

### Key Behavioral Differences

| Feature | Classic Mode | Named Mode |
|---------|-------------|-----------|
| Process identifier | AS number | Name string |
| IPv6 support | Separate `ipv6 router eigrp` process | Integrated AF under one process |
| Per-AF tuning | Not possible | Per-AF bandwidth, timers, K-values |
| EIGRP router-id | Auto-selected from highest loopback | Auto-selected, but set explicitly per AF |

**Skills this lab develops:**

| Skill | Description |
|-------|-------------|
| Named mode structure | Hierarchical `router eigrp NAME` with address-family blocks |
| IPv4 address family | Requires `network` statements and `no auto-summary` |
| IPv6 address family | No `network` needed — activates on all IPv6 interfaces |
| IPv6 prerequisites | `ipv6 unicast-routing` global + explicit `eigrp router-id` in IPv6 AF |
| Classic → Named migration | Remove classic process, rebuild under named mode; brief adjacency reset |

---

## Section 2 — Topology

### Network Diagram

```
                     ┌──────────────────────────────────────┐
                     │                R1                    │
                     │  Lo0: 10.0.0.1/32                    │
                     │       2001:db8::1/128                │
                     │  Hub / Core                          │
                     │  c7200 | IOS 15.3(3)XB12             │
                     └──────────┬──────────────┬────────────┘
                            fa0/0            fa1/0
                         10.12.0.1        10.13.0.1
                       2001:db8:12::1   2001:db8:13::1
                              │                │
           ┌──────────────────┘                └───────────────────┐
           │ 10.12.0.0/30                          10.13.0.0/30    │
           │ 2001:db8:12::/64                      2001:db8:13::/64│
           │                                                        │
┌──────────┴────────────────────┐      ┌────────────────────────────┴────┐
│              R2               │      │              R3                 │
│  Lo0: 10.0.0.2/32             │      │  Lo0: 10.0.0.3/32              │
│       2001:db8::2/128         │      │       2001:db8::3/128          │
│  Branch A                     │      │  Branch B                      │
│  c7200 | IOS 15.3(3)XB12     │      │  c7200 | IOS 15.3(3)XB12      │
└──────────────┬────────────────┘      └───────────────┬────────────────┘
            fa0/1                                    fa0/1
         10.23.0.1                               10.23.0.2
       2001:db8:23::1                          2001:db8:23::2
                  └──────────── 10.23.0.0/30 ─────────────┘
                                2001:db8:23::/64
```

### Cabling Table

| Link ID | Source | Source Interface | Destination | Destination Interface | IPv4 Subnet | IPv6 Subnet |
|---------|--------|------------------|-------------|----------------------|-------------|-------------|
| L1 | R1 | fa0/0 | R2 | fa0/0 | 10.12.0.0/30 | 2001:db8:12::/64 |
| L2 | R1 | fa1/0 | R3 | fa0/0 | 10.13.0.0/30 | 2001:db8:13::/64 |
| L3 | R2 | fa0/1 | R3 | fa0/1 | 10.23.0.0/30 | 2001:db8:23::/64 |

### Console Access Table

| Router | Role | Console (Telnet) | Loopback0 IPv4 | Loopback0 IPv6 |
|--------|------|-----------------|----------------|----------------|
| R1 | Hub / Core | 127.0.0.1:5001 | 10.0.0.1/32 | 2001:db8::1/128 |
| R2 | Branch A | 127.0.0.1:5002 | 10.0.0.2/32 | 2001:db8::2/128 |
| R3 | Branch B | 127.0.0.1:5003 | 10.0.0.3/32 | 2001:db8::3/128 |

---

## Section 3 — Hardware

### Platform Specifications

All routers use **Cisco 7200 (c7200)** with **IOS 15.3(3)XB12**. Named mode EIGRP requires IOS 15.0+.

| Router | Slot 0 | Slot 1 | Active Interfaces |
|--------|--------|--------|-------------------|
| R1 | C7200-IO-FE → fa0/0 | PA-2FE-TX → fa1/0, fa1/1 | fa0/0, fa1/0, Lo0 |
| R2 | C7200-IO-2FE → fa0/0, fa0/1 | — | fa0/0, fa0/1, Lo0 |
| R3 | C7200-IO-2FE → fa0/0, fa0/1 | — | fa0/0, fa0/1, Lo0 |

---

## Section 4 — Base Configuration

Push the initial state to all routers:

```bash
python3 setup_lab.py
```

**Pre-loaded (do not reconfigure):**
- Hostnames, `no ip domain-lookup`
- `ipv6 unicast-routing`
- All IPv4 and IPv6 interface addresses
- EIGRP classic mode AS 100 (running — your task is to migrate it)

**NOT pre-loaded — this is your task:**
- Named mode EIGRP process (ENARSI)
- IPv4 address family configuration
- IPv6 address family configuration

---

## Section 5 — Challenge

### Scenario

> Acme Corp is standardising all routing deployments on EIGRP Named Mode to prepare for multi-AF management and future IPv6-only segments. As the lead network engineer, you must migrate the existing classic EIGRP configuration to named mode and bring up the IPv6 address family across all three routers. A full dual-stack routing table must be operational before the maintenance window closes.

---

### Task 1: Named Mode Process Creation

- Remove the existing classic EIGRP process from all three routers.
- Create a named EIGRP process called **ENARSI** on all three routers.
- Assign each router an explicit EIGRP router ID matching its Loopback0 IPv4 address.

**Verification:** `show ip protocols` must report a routing protocol named "eigrp 100" associated with process ENARSI, with the correct router ID on each router.

---

### Task 2: IPv4 Address Family

- Under the ENARSI process, activate the IPv4 unicast address family using Autonomous System 100.
- Advertise each router's directly connected IPv4 subnets — only subnets reachable via that router's own interfaces.
- Disable automatic summarization.

**Verification:** `show ip eigrp neighbors` must show 2 active neighbors on each router. `show ip route eigrp` must show all remote IPv4 loopback prefixes as `D` routes with Administrative Distance 90.

---

### Task 3: IPv6 Address Family

- Under the ENARSI process, activate the IPv6 unicast address family using Autonomous System 100.
- The IPv6 address family does not use network statements — it activates automatically on all interfaces that have IPv6 addresses assigned.
- Assign an explicit EIGRP router ID for the IPv6 address family on each router.

**Verification:** `show ipv6 eigrp neighbors` must show 2 active neighbors on each router. `show ipv6 route eigrp` must show all remote IPv6 loopback prefixes as `D` routes.

---

### Task 4: Dual-Stack End-to-End Reachability

- Confirm complete dual-stack reachability across all three routers.
- All Loopback0 IPv4 addresses (10.0.0.1, 10.0.0.2, 10.0.0.3) must be reachable from every router, sourced from that router's Loopback0.
- All Loopback0 IPv6 addresses (2001:db8::1, 2001:db8::2, 2001:db8::3) must be reachable from every router, sourced from that router's Loopback0.

**Verification:** All twelve Loopback0-to-Loopback0 pings (6 IPv4 + 6 IPv6) must return 100% success (5/5).

---

## Section 6 — Verification

### Step-by-Step Verification Sequence

#### 1. Verify Named Mode Process

```
R1# show ip protocols
```

Expected — process name ENARSI, AS 100, correct router ID:

```
*** IP Routing is NSF aware ***

Routing Protocol is "eigrp 100"
  Outgoing update filter list for all interfaces is not set
  Incoming update filter list for all interfaces is not set
  Default networks flagged in outgoing updates
  EIGRP-IPv4 VR(ENARSI) Address-Family Protocol for AS(100)    ! ← named mode, AS 100
    Metric weight K1=1, K2=0, K3=1, K4=0, K5=0
    Router-ID: 10.0.0.1                                        ! ← matches Lo0
```

#### 2. Verify IPv4 Neighbors

```
R1# show ip eigrp neighbors
```

Expected — two neighbors, same as Lab 01:

```
EIGRP-IPv4 VR(ENARSI) Address-Family Neighbors for AS(100)    ! ← confirms named mode
H   Address         Interface       Hold Uptime   SRTT   RTO  Q  Seq
                                    (sec)         (ms)       Cnt Num
1   10.13.0.2       Fa1/0             12 00:01:05    5   200  0   3
0   10.12.0.2       Fa0/0             14 00:01:10    5   200  0   5
```

#### 3. Verify IPv6 Neighbors

```
R1# show ipv6 eigrp neighbors
```

Expected — two IPv6 neighbors:

```
EIGRP-IPv6 VR(ENARSI) Address-Family Neighbors for AS(100)    ! ← IPv6 AF
H   Address                 Interface       Hold Uptime   SRTT   RTO
                                            (sec)         (ms)
1   Link-local addr         Fa1/0             11 00:00:58    8   200  ! ← R3
0   Link-local addr         Fa0/0             13 00:01:02    6   200  ! ← R2
```

#### 4. Verify IPv4 Routes

```
R1# show ip route eigrp
```

Expected — same D routes as Lab 01:

```
D    10.0.0.2/32 [90/130816] via 10.12.0.2, FastEthernet0/0  ! ← R2 loopback
D    10.0.0.3/32 [90/130816] via 10.13.0.2, FastEthernet1/0  ! ← R3 loopback
D    10.23.0.0/30 [90/30720] via 10.12.0.2, FastEthernet0/0  ! ← R2-R3 link
                  [90/30720] via 10.13.0.2, FastEthernet1/0
```

#### 5. Verify IPv6 Routes

```
R1# show ipv6 route eigrp
```

Expected — D routes for remote IPv6 loopbacks and links:

```
D   2001:DB8::2/128 [90/130816]                               ! ← R2 loopback
     via FE80::..., FastEthernet0/0
D   2001:DB8::3/128 [90/130816]                               ! ← R3 loopback
     via FE80::..., FastEthernet1/0
D   2001:DB8:23::/64 [90/30720]                               ! ← R2-R3 link
     via FE80::..., FastEthernet0/0
```

#### 6. Verify Dual-Stack Reachability

```
R1# ping 10.0.0.2 source Loopback0
R1# ping 10.0.0.3 source Loopback0
R1# ping 2001:db8::2 source Loopback0
R1# ping 2001:db8::3 source Loopback0
```

Repeat from R2 and R3 for all remote Loopback0 addresses. All twelve pings must return `!!!!!`.

---

## Section 7 — Cheatsheet

### Named Mode Process Structure

```
router eigrp <NAME>
 address-family ipv4 unicast autonomous-system <AS>
  network <address> <wildcard>
  eigrp router-id <ipv4-address>
  no auto-summary
 exit-address-family
 address-family ipv6 unicast autonomous-system <AS>
  eigrp router-id <ipv4-address>
 exit-address-family
```

| Command | Purpose |
|---------|---------|
| `router eigrp <NAME>` | Create a named EIGRP process |
| `address-family ipv4 unicast autonomous-system <AS>` | Enter IPv4 AF; sets the AS number |
| `address-family ipv6 unicast autonomous-system <AS>` | Enter IPv6 AF; no network statements needed |
| `eigrp router-id <ipv4>` | Set explicit router ID within an AF |
| `exit-address-family` | Return to process-level config |

> **Exam tip:** In named mode, `eigrp router-id` is configured **inside** each address family, not at the process level. The IPv6 AF requires it explicitly — EIGRP router IDs are always 32-bit IPv4 values even for IPv6 EIGRP.

### IPv6 Routing Prerequisite

```
ipv6 unicast-routing
```

| Command | Purpose |
|---------|---------|
| `ipv6 unicast-routing` | Globally enable IPv6 routing — required before any IPv6 routing protocol functions |
| `ipv6 address <prefix>` | Assign IPv6 address to an interface (also enables IPv6 on that interface) |

> **Exam tip:** `ipv6 unicast-routing` is a global command. Forgetting it is the most common cause of IPv6 EIGRP adjacencies failing to form even when the AF is correctly configured.

### Migration Commands

```
no router eigrp <AS>
```

| Action | Command |
|--------|---------|
| Remove classic process | `no router eigrp <AS>` (global config mode) |
| Verify no classic process remains | `show run \| section router eigrp` |

### Verification Commands

| Command | What to Look For |
|---------|-----------------|
| `show ip protocols` | Process name ENARSI, AS 100, correct router-id |
| `show ip eigrp neighbors` | "VR(ENARSI)" in header; 2 neighbors per router |
| `show ipv6 eigrp neighbors` | "VR(ENARSI)" in header; 2 IPv6 neighbors per router |
| `show ip route eigrp` | `D` routes for all remote IPv4 prefixes |
| `show ipv6 route eigrp` | `D` routes for all remote IPv6 prefixes |
| `show eigrp address-family ipv4 neighbors` | Alternative AF-specific neighbor view |
| `show eigrp address-family ipv6 neighbors` | Alternative AF-specific neighbor view |
| `show run \| section router eigrp` | Confirm named process; confirm classic process is gone |

### Common Named Mode Failure Causes

| Symptom | Likely Cause |
|---------|-------------|
| IPv4 neighbors missing after migration | Classic `router eigrp <AS>` not removed before adding named mode |
| IPv6 neighbors never form | `ipv6 unicast-routing` missing on one or more routers |
| IPv6 AF configured but no adjacency | `eigrp router-id` missing in IPv6 AF |
| IPv4 AF adjacency drops | AS number mismatch in `address-family ipv4 unicast autonomous-system` |
| Both AFs fail simultaneously | K-value mismatch between routers |

---

## Section 8 — Solutions

<details>
<summary>R1 — Complete Solution Configuration (click to expand)</summary>

```
!
hostname R1
!
no ip domain-lookup
!
ipv6 unicast-routing
!
interface Loopback0
 description Lo0 - Router ID
 ip address 10.0.0.1 255.255.255.255
 ipv6 address 2001:DB8::1/128
!
interface FastEthernet0/0
 description Link to R2 fa0/0 -- 10.12.0.0/30
 ip address 10.12.0.1 255.255.255.252
 ipv6 address 2001:DB8:12::1/64
 no shutdown
!
interface FastEthernet1/0
 description Link to R3 fa0/0 -- 10.13.0.0/30
 ip address 10.13.0.1 255.255.255.252
 ipv6 address 2001:DB8:13::1/64
 no shutdown
!
router eigrp ENARSI
 !
 address-family ipv4 unicast autonomous-system 100
  eigrp log-neighbor-changes
  network 10.12.0.0 0.0.0.3
  network 10.13.0.0 0.0.0.3
  network 10.0.0.1 0.0.0.0
  eigrp router-id 10.0.0.1
  no auto-summary
 exit-address-family
 !
 address-family ipv6 unicast autonomous-system 100
  eigrp log-neighbor-changes
  eigrp router-id 10.0.0.1
 exit-address-family
!
end
```

</details>

<details>
<summary>R2 — Complete Solution Configuration (click to expand)</summary>

```
!
hostname R2
!
no ip domain-lookup
!
ipv6 unicast-routing
!
interface Loopback0
 description Lo0 - Router ID
 ip address 10.0.0.2 255.255.255.255
 ipv6 address 2001:DB8::2/128
!
interface FastEthernet0/0
 description Link to R1 fa0/0 -- 10.12.0.0/30
 ip address 10.12.0.2 255.255.255.252
 ipv6 address 2001:DB8:12::2/64
 no shutdown
!
interface FastEthernet0/1
 description Link to R3 fa0/1 -- 10.23.0.0/30
 ip address 10.23.0.1 255.255.255.252
 ipv6 address 2001:DB8:23::1/64
 no shutdown
!
router eigrp ENARSI
 !
 address-family ipv4 unicast autonomous-system 100
  eigrp log-neighbor-changes
  network 10.12.0.0 0.0.0.3
  network 10.23.0.0 0.0.0.3
  network 10.0.0.2 0.0.0.0
  eigrp router-id 10.0.0.2
  no auto-summary
 exit-address-family
 !
 address-family ipv6 unicast autonomous-system 100
  eigrp log-neighbor-changes
  eigrp router-id 10.0.0.2
 exit-address-family
!
end
```

</details>

<details>
<summary>R3 — Complete Solution Configuration (click to expand)</summary>

```
!
hostname R3
!
no ip domain-lookup
!
ipv6 unicast-routing
!
interface Loopback0
 description Lo0 - Router ID
 ip address 10.0.0.3 255.255.255.255
 ipv6 address 2001:DB8::3/128
!
interface FastEthernet0/0
 description Link to R1 fa1/0 -- 10.13.0.0/30
 ip address 10.13.0.2 255.255.255.252
 ipv6 address 2001:DB8:13::2/64
 no shutdown
!
interface FastEthernet0/1
 description Link to R2 fa0/1 -- 10.23.0.0/30
 ip address 10.23.0.2 255.255.255.252
 ipv6 address 2001:DB8:23::2/64
 no shutdown
!
router eigrp ENARSI
 !
 address-family ipv4 unicast autonomous-system 100
  eigrp log-neighbor-changes
  network 10.13.0.0 0.0.0.3
  network 10.23.0.0 0.0.0.3
  network 10.0.0.3 0.0.0.0
  eigrp router-id 10.0.0.3
  no auto-summary
 exit-address-family
 !
 address-family ipv6 unicast autonomous-system 100
  eigrp log-neighbor-changes
  eigrp router-id 10.0.0.3
 exit-address-family
!
end
```

</details>

---

## Section 9 — Troubleshooting

> **Instructions:** Inject the fault, then diagnose from symptoms using `show` commands only. Do not read the fault script `README.md` before attempting.

### Ticket 09-1: Branch A Has No IPv4 Routing Peers

**Reported by:** NOC
**Severity:** Critical
**Symptom:** `show ip eigrp neighbors` on R2 returns empty. R1 and R3 have a working IPv4 adjacency with each other. IPv4 pings from R2 to R1 and R3 loopbacks fail. IPv6 adjacencies on R2 appear to be functioning normally. EIGRP named mode is confirmed configured on R2.

**To inject this fault:**
```bash
python3 scripts/fault-injection/inject_scenario_01.py
```

---

### Ticket 09-2: Branch B Has No IPv6 Routes

**Reported by:** IPv6 Migration Team
**Severity:** High
**Symptom:** `show ipv6 eigrp neighbors` on R3 is empty. R1 and R2 show each other as IPv6 EIGRP neighbors but neither shows R3. IPv4 adjacencies on all three links are fully operational. IPv6 addresses are confirmed on all R3 interfaces. `show ipv6 route` on R3 shows only connected routes, no EIGRP `D` entries.

**To inject this fault:**
```bash
python3 scripts/fault-injection/inject_scenario_02.py
```

---

### Ticket 09-3: R3 Loopback Invisible on IPv4

**Reported by:** Server Team
**Severity:** Medium
**Symptom:** All six EIGRP adjacencies (IPv4 and IPv6) are Up. R1 and R2 can ping R3's physical IPv4 interfaces successfully. Pings to R3's loopback (10.0.0.3) fail from both R1 and R2. The 10.0.0.3/32 prefix is absent from R1 and R2's IPv4 routing tables. R3's own routing table shows its loopback as directly connected.

**To inject this fault:**
```bash
python3 scripts/fault-injection/inject_scenario_03.py
```

---

## Section 10 — Completion Checklist

**Named Mode Process**
- [ ] `show ip protocols` on all routers — process ENARSI, AS 100, router-id matches Lo0
- [ ] `show run | section router eigrp` — no classic `router eigrp 100` remains on any router

**IPv4 Address Family**
- [ ] `show ip eigrp neighbors` on R1 — 2 neighbors (R2 fa0/0, R3 fa1/0)
- [ ] `show ip eigrp neighbors` on R2 — 2 neighbors (R1 fa0/0, R3 fa0/1)
- [ ] `show ip eigrp neighbors` on R3 — 2 neighbors (R1 fa0/0, R2 fa0/1)
- [ ] `show ip route eigrp` on R1 — D routes for 10.0.0.2/32, 10.0.0.3/32, 10.23.0.0/30
- [ ] `show ip route eigrp` on R2 — D routes for 10.0.0.1/32, 10.0.0.3/32, 10.13.0.0/30
- [ ] `show ip route eigrp` on R3 — D routes for 10.0.0.1/32, 10.0.0.2/32, 10.12.0.0/30

**IPv6 Address Family**
- [ ] `show ipv6 eigrp neighbors` on R1 — 2 IPv6 neighbors
- [ ] `show ipv6 eigrp neighbors` on R2 — 2 IPv6 neighbors
- [ ] `show ipv6 eigrp neighbors` on R3 — 2 IPv6 neighbors
- [ ] `show ipv6 route eigrp` on R1 — D routes for 2001:db8::2/128, 2001:db8::3/128, 2001:db8:23::/64
- [ ] `show ipv6 route eigrp` on R2 — D routes for 2001:db8::1/128, 2001:db8::3/128, 2001:db8:13::/64
- [ ] `show ipv6 route eigrp` on R3 — D routes for 2001:db8::1/128, 2001:db8::2/128, 2001:db8:12::/64

**Dual-Stack Reachability**
- [ ] `ping 10.0.0.2/3 source Lo0` from R1 — 5/5 success
- [ ] `ping 10.0.0.1/3 source Lo0` from R2 — 5/5 success
- [ ] `ping 10.0.0.1/2 source Lo0` from R3 — 5/5 success
- [ ] `ping 2001:db8::2/3 source Lo0` from R1 — 5/5 success
- [ ] `ping 2001:db8::1/3 source Lo0` from R2 — 5/5 success
- [ ] `ping 2001:db8::1/2 source Lo0` from R3 — 5/5 success

**Troubleshooting Tickets**
- [ ] Ticket 09-1 (Branch A No IPv4 Peers) — diagnosed and resolved
- [ ] Ticket 09-2 (Branch B No IPv6 Routes) — diagnosed and resolved
- [ ] Ticket 09-3 (R3 Loopback Invisible on IPv4) — diagnosed and resolved
