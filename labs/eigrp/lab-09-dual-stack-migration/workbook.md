# CCNP ENCOR EIGRP Lab 09: Dual-Stack EIGRP Migration
**Student Workbook & Instructor Guide**

---

## 1. Concepts & Skills Covered

- Configure Legacy IPv6 EIGRP on c3725 routers (IOS 12.4) using `ipv6 router eigrp`
- Configure EIGRP Named Mode on c7200 routers (IOS 15.3) with dual address families
- Understand that Named Mode and Classic Mode are fully interoperable at the protocol level
- Understand that c3725 (IOS 12.4) does **not** support EIGRP Named Mode
- Verify dual-stack EIGRP adjacencies and route propagation across a mixed IOS environment
- Implement EIGRP stub for IPv6 on c3725 using `eigrp stub` under `ipv6 router eigrp`
- Configure IPv4 route summarization on c3725 using `ip summary-address eigrp` on the interface

---

## 2. Topology & Scenario

### ASCII Diagram
```
                                  ┌─────────────────┐
                                  │       R4        │
                                  │  OSPF Domain    │
                                  │  4.4.4.4/32     │
                                  └────────┬────────┘
                                           │ Fa0/0
                                           │ 10.0.14.2/30
                                           │
                    ┌─────────────────┐    │ Fa1/1
                    │       R1        ├────┘
                    │   (Hub Router)  ├──────────────┐
                    │  Lo0: 1.1.1.1   │              │ Fa0/0
                    └───┬─────────┬───┘              │ 10.0.17.1/30
                        │ Fa1/0   │ Fa1/1            │
                        │         │                  │
           10.0.12.1/30 │         │ 10.0.12.2/30     │ 10.0.17.2/30
                        │    ┌────┴────────┐    ┌────┴────────┐
                        │    │     R2      │    │     R7      │
                        │    │   Branch    │    │ Summary Bdy │
                        │    │ 2.2.2.2/32  │    │ 7.7.7.7/32  │
                        │    └────┬────────┘    └─────────────┘
                        │         │ Fa0/1
                        │         │ 10.0.23.1/30
                        │         │
                        │         │ 10.0.23.2/30
                        │         │ Fa0/0
                 ┌──────┴─────────┘
                 │       R3
                 │  Remote Branch
                 │  3.3.3.3/32
                 └───┬─────────┐
                     │ Fa0/1   │
                     │         │ 10.0.35.1/30
                     │         │
                     │         │ 10.0.35.2/30
                     │         │ Fa0/0
              ┌──────┴─────────┘
              │       R5
              │   Stub Network
              │  5.5.5.5/32
              └─────────────────┘
                                  ┌─────────────────┐
                                  │       R6        │
                                  │  VPN Endpoint   │
                                  │  6.6.6.6/32     │
                                  └────────┬────────┘
                                           │ Gi3/0 (Physical + Tunnel8)
```

### Scenario Narrative
The **Skynet Global** network is entering its final phase of infrastructure modernization — the **Dual-Stack (IPv4/IPv6)** initiative. Your task is to enable IPv6 EIGRP routing across the entire domain while working within the constraints of the installed hardware.

The network team has identified a critical platform limitation: **Cisco 3725 routers running IOS 12.4 do not support EIGRP Named Mode**. Named Mode requires IOS 15.0(1)M or later. Only the Cisco 7200 routers (R1 and R6) running IOS 15.3 can use Named Mode.

The architecture is therefore **split-mode**:
- **R1, R6 (c7200 / IOS 15.3)** → EIGRP Named Mode with `address-family ipv4` and `address-family ipv6`
- **R2, R3, R5, R7 (c3725 / IOS 12.4)** → Classic Mode IPv4 (`router eigrp 100`) + Legacy IPv6 EIGRP (`ipv6 router eigrp 100`)

> **Key Concept:** Named Mode and Classic Mode are **protocol-compatible**. The EIGRP PDU format is identical. A c7200 running `router eigrp SKYNET_CORE` with `address-family ipv4 autonomous-system 100` forms adjacencies normally with a c3725 running `router eigrp 100`. There is no migration required on the c3725 routers — they remain in Classic Mode for IPv4 and use Legacy IPv6 EIGRP for IPv6.

### Device Role Table
| Device | Role | Platform | IOS | Loopback0 | EIGRP Mode | New in Lab 09 |
|--------|------|----------|-----|-----------|-----------|---------------|
| R1 | Hub / EIGRP Lead | c7200 | 15.3 | 1.1.1.1/32 | Named Mode | No |
| R2 | Branch Router | c3725 | 12.4 | 2.2.2.2/32 | Classic + Legacy IPv6 | No |
| R3 | Remote Branch | c3725 | 12.4 | 3.3.3.3/32 | Classic + Legacy IPv6 | No |
| R4 | CyberDyne OSPF | c3725 | 12.4 | 4.4.4.4/32 | OSPF only | No |
| R5 | Stub Network | c3725 | 12.4 | 5.5.5.5/32 | Classic + Legacy IPv6 | No |
| R6 | VPN Endpoint | c7200 | 15.3 | 6.6.6.6/32 | Named Mode | No |
| R7 | Summary Boundary | c3725 | 12.4 | 7.7.7.7/32 | Classic + Legacy IPv6 | **Yes** |

---

## 3. Hardware & Environment Specifications

### 3.1 Router Platform Table
| Device | Model | RAM | Image Name |
|--------|-------|-----|------------|
| R1 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |
| R2-R5, R7 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R6 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |

### 3.2 Cabling & Connectivity Table
| Local Device | Local Interface | Remote Device | Remote Interface | Subnet |
|--------------|-----------------|---------------|------------------|--------|
| R1           | Fa1/0           | R2            | Fa0/0            | 10.0.12.0/30 |
| R2           | Fa0/1           | R3            | Fa0/0            | 10.0.23.0/30 |
| R3           | Fa0/1           | R5            | Fa0/0            | 10.0.35.0/30 |
| R1           | Fa1/1           | R4            | Fa0/0            | 10.0.14.0/30 |
| R1           | Gi3/0           | R6            | Gi3/0            | 10.0.16.0/30 |
| R1           | Fa0/0           | R7            | Fa0/0            | 10.0.17.0/30 |
| R1           | Tunnel8         | R6            | Tunnel8          | 172.16.16.0/30 |

### 3.3 Console Access Table
| Device | Port | Connection Command |
|--------|------|--------------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |
| R4 | 5004 | `telnet 127.0.0.1 5004` |
| R5 | 5005 | `telnet 127.0.0.1 5005` |
| R6 | 5006 | `telnet 127.0.0.1 5006` |
| R7 | 5007 | `telnet 127.0.0.1 5007` |

---

## 4. Base Configuration

> ⚠️ **This lab builds on Lab 08.** Ensure that the GRE tunnel and previous redistribution/security settings are functional before proceeding.

### R7 (Summary Boundary — New to Lab 09)
```bash
enable
configure terminal
hostname R7
interface Loopback0
 ip address 7.7.7.7 255.255.255.255
interface FastEthernet0/0
 ip address 10.0.17.2 255.255.255.252
 no shutdown
router eigrp 100
 network 7.7.7.7 0.0.0.0
 network 10.0.17.0 0.0.0.3
end
```

---

## 5. Lab Challenge: NextGen Dual-Stack Migration

### Objective 1: Upgrade c7200 Routers to Named Mode (R1 and R6)
Convert the existing Classic Mode EIGRP configuration on **R1** and **R6** to Named Mode. This is only possible on these routers because they run IOS 15.3.

- Use the virtual instance name `SKYNET_CORE`.
- Migrate the IPv4 AS 100 settings into `address-family ipv4 autonomous-system 100` sub-mode.
- Remove the old `router eigrp 100` process only after verifying Named Mode is operational.
- Verify that EIGRP neighbors re-establish and all routes are present.

> **Note:** The c3725 routers (R2, R3, R5, R7) **remain in Classic Mode** (`router eigrp 100`). No Named Mode migration is needed or possible on these platforms.

### Objective 2: Enable Dual-Stack IPv6 EIGRP

Deploy IPv6 addressing and EIGRP across the domain using the correct method per platform.

**Addressing Scheme:**
- Loopbacks: `2001:DB8:ACAD:<Device#>::<Device#>/128`
- Links: `2001:DB8:ACAD:<Subnet-ID>::/64` (e.g., link 12 → `2001:DB8:ACAD:12::/64`)
- Tunnel8: `2001:DB8:ACAD:88::/64`

Enable `ipv6 unicast-routing` globally on **all** routers.

**For R1 and R6 (c7200 / Named Mode):**
- Add an `address-family ipv6 autonomous-system 100` block under `router eigrp SKYNET_CORE`.
- Assign IPv6 addresses to all active interfaces — Named Mode activates EIGRP on them automatically.

**For R2, R3, R5, R7 (c3725 / Legacy IPv6 EIGRP):**
- Configure `ipv6 router eigrp 100` globally and set `eigrp router-id`.
- Assign IPv6 addresses to all active interfaces.
- Enable EIGRP on each interface with `ipv6 eigrp 100` (this is the legacy per-interface activation method).

### Objective 3: Dual-Stack Verification
- Verify that every router has both an IPv4 and IPv6 routing table with full reachability.
- On **R1** (Named Mode), use `show eigrp address-family ipv4 neighbors` and `show eigrp address-family ipv6 neighbors`.
- On **R2** (Classic/Legacy), use `show ip eigrp neighbors` and `show ipv6 eigrp neighbors`.
- Confirm reachability to all loopbacks via both protocols using `ping` and `ping ipv6`.

### Objective 4: Optimization & Advanced AF Features
- On **R7**, configure a summary route for `10.0.0.0/8` towards R1.
  - In Classic Mode (c3725), use the **interface-level** command: `ip summary-address eigrp 100 10.0.0.0 255.0.0.0`
- On **R5**, verify that the stub configuration is active for both IPv4 and IPv6.
  - IPv4 stub: `eigrp stub connected summary` under `router eigrp 100` (already present).
  - IPv6 stub: `eigrp stub connected summary` under `ipv6 router eigrp 100`.

---

## 6. Verification & Analysis

### Named Mode Verification (R1, R6 — c7200)
| Command | Expected Outcome |
|---------|------------------|
| `show eigrp address-family ipv4 neighbors` | IPv4 neighbors listed under VR(SKYNET_CORE). |
| `show eigrp address-family ipv6 neighbors` | IPv6 neighbors listed via link-local address. |
| `show eigrp address-family ipv4 topology` | Full IPv4 topology table. |
| `show eigrp address-family ipv6 topology` | Full IPv6 topology table. |

### Legacy Verification (R2, R3, R5, R7 — c3725)
| Command | Expected Outcome |
|---------|------------------|
| `show ip eigrp neighbors` | IPv4 EIGRP neighbors (Classic Mode). |
| `show ipv6 eigrp neighbors` | IPv6 EIGRP neighbors (Legacy Mode). |
| `show ipv6 route eigrp` | IPv6 routes learned via EIGRP. |
| `show ipv6 eigrp interfaces` | Interfaces participating in Legacy IPv6 EIGRP. |

### End-to-End Verification (Any Router)
| Command | Expected Outcome |
|---------|------------------|
| `ping ipv6 2001:DB8:ACAD:5::5` | Successful IPv6 ping to R5 loopback. |
| `show ipv6 route eigrp` | IPv6 D-routes present across the domain. |

---

## 7. Verification Cheatsheet

### 7.1 Verify IPv4 Named Mode Neighbors (R1)
```bash
R1# show eigrp address-family ipv4 neighbors
EIGRP-IPv4 VR(SKYNET_CORE) Address-Family Neighbors for AS(100)
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   10.0.12.2               Fa1/0                    12 00:10:25   15   200  0  55
1   10.0.17.2               Fa0/0                    11 00:08:42   18   200  0  20
2   172.16.16.2             Tu8                      14 00:09:11   22   200  0  33
```
*Verify: Neighbors from R2 (Fa1/0), R7 (Fa0/0), and R6 (Tunnel8) are all listed under VR(SKYNET_CORE).*

### 7.2 Verify IPv6 Named Mode Neighbors (R1)
```bash
R1# show eigrp address-family ipv6 neighbors
EIGRP-IPv6 VR(SKYNET_CORE) Address-Family Neighbors for AS(100)
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   FE80::C802:12FF:FE34:0  Fa1/0                    14 00:05:12   20   200  0  12
1   FE80::C807:17FF:FE00:0  Fa0/0                    13 00:04:55   18   200  0   8
2   FE80::C806:16FF:FE00:0  Tu8                      12 00:04:33   25   200  0  15
```
*Verify: IPv6 neighbors established via link-local addresses on all interfaces.*

### 7.3 Verify Legacy IPv6 Neighbors (R2 — c3725)
```bash
R2# show ipv6 eigrp neighbors
EIGRP-IPv6 Neighbors for AS(100)
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   FE80::C801:12FF:FE00:0  Fa0/0                    14 00:05:12   20   200  0  12
1   FE80::C803:23FF:FE00:0  Fa0/1                    11 00:04:50   22   200  0   9
```
*Verify: R2 shows R1 (via Fa0/0) and R3 (via Fa0/1) as Legacy IPv6 EIGRP neighbors.*

### 7.4 Verify IPv6 Reachability
```bash
R1# ping ipv6 2001:DB8:ACAD:5::5
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 2001:DB8:ACAD:5::5, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 20/24/32 ms
```

### 7.5 Verify IPv6 EIGRP Interfaces on c3725
```bash
R2# show ipv6 eigrp interfaces
EIGRP-IPv6 Interfaces for AS(100)

                        Xmit Queue   Mean   Pacing Time   Multicast    Pending
Interface        Peers  Un/Reliable  SRTT   Un/Reliable   Flow Timer   Routes
Fa0/0              1        0/0        20       0/1           50           0
Fa0/1              1        0/0        22       0/1           50           0
Lo0                0        0/0         5       0/1           50           0
```
*Verify: Fa0/0, Fa0/1, and Lo0 are all participating in Legacy IPv6 EIGRP (enabled via `ipv6 eigrp 100`).*

---

## 8. Troubleshooting Scenario

### The Fault
After configuring Named Mode on R1 and R6, and enabling Legacy IPv6 EIGRP on all c3725 routers, the GRE tunnel between R1 and R6 carries IPv4 EIGRP traffic normally but **R6's IPv6 loopback does not appear in R1's IPv6 routing table**.

### The Mission
1. Verify that `Tunnel8` on R6 has an IPv6 address assigned (`2001:DB8:ACAD:88::2/64`).
2. Confirm `ipv6 unicast-routing` is enabled on R6.
3. Ensure the `address-family ipv6` block is active under `router eigrp SKYNET_CORE` on R6.
4. Check whether `ipv6 enable` is set on `Tunnel8` in addition to the explicit IPv6 address.

---

## 9. Solutions (Spoiler Alert!)

### Objective 1 & 2: Named Mode Migration + IPv6 (R1 — c7200)

<details>
<summary>Click to view R1 Configuration</summary>

```bash
ipv6 unicast-routing
!
interface Loopback0
 ip address 1.1.1.1 255.255.255.255
 ipv6 address 2001:DB8:ACAD:1::1/128
 ipv6 enable
!
interface FastEthernet1/0
 ip address 10.0.12.1 255.255.255.252
 ipv6 address 2001:DB8:ACAD:12::1/64
 ipv6 enable
!
interface FastEthernet0/0
 ip address 10.0.17.1 255.255.255.252
 ipv6 address 2001:DB8:ACAD:17::1/64
 ipv6 enable
!
interface GigabitEthernet3/0
 ip address 10.0.16.1 255.255.255.252
 ipv6 address 2001:DB8:ACAD:16::1/64
 ipv6 enable
!
interface Tunnel8
 ip address 172.16.16.1 255.255.255.252
 ipv6 address 2001:DB8:ACAD:88::1/64
 ipv6 enable
!
router eigrp SKYNET_CORE
 address-family ipv4 autonomous-system 100
  network 1.1.1.1 0.0.0.0
  network 10.0.12.0 0.0.0.3
  network 10.0.17.0 0.0.0.3
  network 172.16.16.0 0.0.0.3
  topology base
  exit-af-topology
 exit-address-family
 !
 address-family ipv6 autonomous-system 100
  topology base
  exit-af-topology
 exit-address-family
```
</details>

### Objective 2: Enable IPv6 (R6 — c7200, Named Mode)

<details>
<summary>Click to view R6 Configuration</summary>

```bash
ipv6 unicast-routing
!
interface Loopback0
 ip address 6.6.6.6 255.255.255.255
 ipv6 address 2001:DB8:ACAD:6::6/128
 ipv6 enable
!
interface GigabitEthernet3/0
 ip address 10.0.16.2 255.255.255.252
 ipv6 address 2001:DB8:ACAD:16::2/64
 ipv6 enable
!
interface Tunnel8
 ip address 172.16.16.2 255.255.255.252
 ipv6 address 2001:DB8:ACAD:88::2/64
 ipv6 enable
 tunnel source 10.0.16.2
 tunnel destination 10.0.16.1
!
router eigrp SKYNET_CORE
 address-family ipv4 autonomous-system 100
  network 6.6.6.6 0.0.0.0
  network 172.16.16.0 0.0.0.3
  topology base
  exit-af-topology
 exit-address-family
 !
 address-family ipv6 autonomous-system 100
  topology base
  exit-af-topology
 exit-address-family
!
ip route 0.0.0.0 0.0.0.0 10.0.16.1
ipv6 route ::/0 2001:DB8:ACAD:16::1
```
</details>

### Objective 2: Enable IPv6 (R2 — c3725, Legacy IPv6 EIGRP)

<details>
<summary>Click to view R2 Configuration</summary>

```bash
ipv6 unicast-routing
!
interface Loopback0
 ip address 2.2.2.2 255.255.255.255
 ipv6 address 2001:DB8:ACAD:2::2/128
 ipv6 eigrp 100
!
interface FastEthernet0/0
 ip address 10.0.12.2 255.255.255.252
 ip authentication mode eigrp 100 md5
 ip authentication key-chain eigrp 100 SKYNET_MD5
 ipv6 address 2001:DB8:ACAD:12::2/64
 ipv6 eigrp 100
!
interface FastEthernet0/1
 ip address 10.0.23.1 255.255.255.252
 ipv6 address 2001:DB8:ACAD:23::1/64
 ipv6 eigrp 100
!
router eigrp 100
 network 2.2.2.2 0.0.0.0
 network 10.0.12.0 0.0.0.3
 network 10.0.23.0 0.0.0.3
 no auto-summary
!
ipv6 router eigrp 100
 eigrp router-id 2.2.2.2
```
</details>

### Objective 2: Enable IPv6 (R3 — c3725, Legacy IPv6 EIGRP)

<details>
<summary>Click to view R3 Configuration</summary>

```bash
ipv6 unicast-routing
!
interface Loopback0
 ip address 3.3.3.3 255.255.255.255
 ipv6 address 2001:DB8:ACAD:3::3/128
 ipv6 eigrp 100
!
interface FastEthernet0/0
 ip address 10.0.23.2 255.255.255.252
 ipv6 address 2001:DB8:ACAD:23::2/64
 ipv6 eigrp 100
!
interface FastEthernet0/1
 ip address 10.0.35.1 255.255.255.252
 ipv6 address 2001:DB8:ACAD:35::1/64
 ipv6 eigrp 100
!
router eigrp 100
 network 3.3.3.3 0.0.0.0
 network 10.0.23.0 0.0.0.3
 network 10.0.35.0 0.0.0.3
 no auto-summary
!
ipv6 router eigrp 100
 eigrp router-id 3.3.3.3
```
</details>

### Objectives 2 & 4: Enable IPv6 + Stub (R5 — c3725, Legacy IPv6 EIGRP)

<details>
<summary>Click to view R5 Configuration</summary>

```bash
ipv6 unicast-routing
!
interface Loopback0
 ip address 5.5.5.5 255.255.255.255
 ipv6 address 2001:DB8:ACAD:5::5/128
 ipv6 eigrp 100
!
interface Loopback1
 ip address 10.5.1.1 255.255.255.0
!
interface Loopback2
 ip address 10.5.2.1 255.255.255.0
!
interface Loopback3
 ip address 10.5.3.1 255.255.255.0
!
interface FastEthernet0/0
 ip address 10.0.35.2 255.255.255.252
 ipv6 address 2001:DB8:ACAD:35::2/64
 ipv6 eigrp 100
!
router eigrp 100
 network 5.5.5.5 0.0.0.0
 network 10.0.35.0 0.0.0.3
 network 10.5.0.0 0.0.255.255
 eigrp stub connected summary
 no auto-summary
!
ipv6 router eigrp 100
 eigrp router-id 5.5.5.5
 eigrp stub connected summary
```
</details>

### Objectives 2 & 4: Enable IPv6 + Summary (R7 — c3725, Legacy IPv6 EIGRP)

<details>
<summary>Click to view R7 Configuration</summary>

```bash
ipv6 unicast-routing
!
interface Loopback0
 ip address 7.7.7.7 255.255.255.255
 ipv6 address 2001:DB8:ACAD:7::7/128
 ipv6 eigrp 100
!
interface FastEthernet0/0
 ip address 10.0.17.2 255.255.255.252
 ip summary-address eigrp 100 10.0.0.0 255.0.0.0
 ipv6 address 2001:DB8:ACAD:17::2/64
 ipv6 eigrp 100
!
router eigrp 100
 network 7.7.7.7 0.0.0.0
 network 10.0.17.0 0.0.0.3
 no auto-summary
!
ipv6 router eigrp 100
 eigrp router-id 7.7.7.7
```
</details>

---

## 10. Lab Completion Checklist

- [ ] R1 and R6 migrated to Named Mode with both IPv4 and IPv6 address families.
- [ ] R2, R3, R5, R7 have Legacy IPv6 EIGRP configured (`ipv6 router eigrp 100` + `ipv6 eigrp 100` on interfaces).
- [ ] `ipv6 unicast-routing` enabled on all routers.
- [ ] IPv6 connectivity established globally (all loopbacks pingable via IPv6).
- [ ] Dual-stack EIGRP adjacencies verified on all links.
- [ ] GRE Tunnel (R1 ↔ R6) carries both IPv4 and IPv6 EIGRP traffic.
- [ ] R5 stub active for both IPv4 and IPv6 (`eigrp stub connected summary` under both EIGRP processes).
- [ ] R7 summarizing 10.0.0.0/8 via `ip summary-address eigrp 100` on Fa0/0.
- [ ] Troubleshooting challenge resolved.
