# CCNP ENCOR EIGRP Lab 03: Route Summarization
**Student Workbook & Instructor Guide**

---

## 1. Concepts & Skills Covered

- Configure manual route summarization on EIGRP
- Understand how summarization creates query boundaries
- Verify summary routes in the topology table
- Analyze the impact of summarization on routing table size
- Troubleshoot summarization misconfigurations
- Integrate a new router (R7) into existing EIGRP domain

---

## 2. Topology & Scenario

### ASCII Diagram
```
                    ┌─────────────────┐
                    │       R1        │
                    │   (Hub Router)  │
                    │  Lo0: 1.1.1.1   │
                    └───┬─────────┬───┘
                        │ Fa1/0   │ Fa0/0
                        │         │ 10.0.17.1/30
                        │         │
         10.0.12.1/30   │         │ 10.0.17.2/30
                        │         │ Fa0/0
                        │    ┌────┴────────┐
                        │    │     R7      │
                        │    │  (Summary   │
                        │    │  Boundary)  │
                        │    │ Lo0: 7.7.7.7│
                        │    └─────────────┘
                        │
                        │ 10.0.12.2/30
                        │ Fa0/0
                ┌───────┴─────────┐
                │       R2        │
                │ (Branch Router) │
                │  Lo0: 2.2.2.2   │
                └───────┬─────────┘
                        │ Fa0/1
                        │ 10.0.23.1/30
                        │
                        │ 10.0.23.2/30
                        │ Fa0/0
                ┌───────┴─────────┐
                │       R3        │
                │ (Remote Branch) │
                │  Lo0: 3.3.3.3   │
                │  + Summary nets │
                └─────────────────┘
```

### Scenario Narrative
Your enterprise network is growing. The routing tables on R1 and R2 are becoming large, and EIGRP queries are propagating across the entire network when a route flaps. You need to implement route summarization to:
1. Reduce routing table size
2. Create query boundaries
3. Improve network stability

A new summary boundary router (R7) has been added to demonstrate summarization behavior.

### Device Role Table
| Device | Role | Platform | Loopback0 | New in Lab 03 |
|--------|------|----------|-----------|---------------|
| R1 | Hub Router | c7200 | 1.1.1.1/32 | No |
| R2 | Branch Router | c3725 | 2.2.2.2/32 | No |
| R3 | Remote Branch | c3725 | 3.3.3.3/32 | No |
| R7 | Summary Boundary | c3725 | 7.7.7.7/32 | **Yes** |

---

## 3. Hardware & Environment Specifications

### Router Platform Table
| Device | Model | RAM | Image Name |
|--------|-------|-----|------------|
| R1 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |
| R2 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R3 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R7 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |

### Console Access Table
| Device | Port | Connection Command |
|--------|------|--------------------|
| R1 | 5001 | `telnet localhost 5001` |
| R2 | 5002 | `telnet localhost 5002` |
| R3 | 5003 | `telnet localhost 5003` |
| R7 | 5007 | `telnet localhost 5007` |

### Cabling Table
| Link ID | Source:Interface | Target:Interface | Subnet | Status |
|---------|------------------|------------------|--------|--------|
| L1 | R1:Fa1/0 | R2:Fa0/0 | 10.0.12.0/30 | Existing |
| L2 | R2:Fa0/1 | R3:Fa0/0 | 10.0.23.0/30 | Existing |
| L6 | R1:Fa0/0 | R7:Fa0/0 | 10.0.17.0/30 | **New** |

---

## 4. Base Configuration

> ⚠️ **This lab builds on Lab 02.** Initial configs include EIGRP from previous labs.

### R1 (Existing + New Interface)
```bash
enable
configure terminal
!
! New interface for R7 connection
interface FastEthernet0/0
 description Link to R7 (Summary Boundary)
 ip address 10.0.17.1 255.255.255.252
 no shutdown
!
end
write memory
```

### R7 (New Device - Complete Config)
```bash
enable
configure terminal
!
hostname R7
!
interface Loopback0
 ip address 7.7.7.7 255.255.255.255
 no shutdown
!
! Simulated summary networks behind R7
interface Loopback1
 ip address 172.16.1.1 255.255.255.0
 no shutdown
!
interface Loopback2
 ip address 172.16.2.1 255.255.255.0
 no shutdown
!
interface Loopback3
 ip address 172.16.3.1 255.255.255.0
 no shutdown
!
interface Loopback4
 ip address 172.16.4.1 255.255.255.0
 no shutdown
!
interface FastEthernet0/0
 description Link to R1 (Hub)
 ip address 10.0.17.2 255.255.255.252
 no shutdown
!
router eigrp 100
 eigrp router-id 7.7.7.7
 network 7.7.7.7 0.0.0.0
 network 10.0.17.0 0.0.0.3
 network 172.16.0.0 0.0.255.255
 no auto-summary
 passive-interface Loopback0
 passive-interface Loopback1
 passive-interface Loopback2
 passive-interface Loopback3
 passive-interface Loopback4
!
line con 0
 logging synchronous
 exec-timeout 0 0
!
end
write memory
```

### R3 - Add Summary Networks
```bash
enable
configure terminal
!
! Add networks to be summarized
interface Loopback1
 ip address 192.168.1.1 255.255.255.0
 no shutdown
!
interface Loopback2
 ip address 192.168.2.1 255.255.255.0
 no shutdown
!
interface Loopback3
 ip address 192.168.3.1 255.255.255.0
 no shutdown
!
router eigrp 100
 network 192.168.0.0 0.0.255.255
 passive-interface Loopback1
 passive-interface Loopback2
 passive-interface Loopback3
!
end
write memory
```

---

## 5. Configuration Tasks Workbook

### Task 1: Verify Current Routing Table Size

**Objective:** Observe the unsummarized routing table before implementing summarization.

**Theory:**
Without summarization, every specific route is advertised individually. This leads to:
- Large routing tables consuming memory
- Longer SPF calculations
- Broader query scope during convergence

**Step-by-Step:**
```bash
! On R1 - Check current routes
show ip route eigrp
show ip route summary

! Count EIGRP routes
show ip route eigrp | count D
```

**Expected:** Multiple /24 and /32 routes for the 172.16.x.x and 192.168.x.x ranges.

---

### Task 2: Configure Summarization on R7

**Objective:** Summarize the 172.16.0.0/16 networks at R7 before advertising to R1.

**Theory:**
EIGRP summarization is configured per-interface using `ip summary-address eigrp`. The summary:
- Creates a Null0 route locally (loop prevention)
- Advertises a single summary instead of component routes
- Establishes a query boundary (queries stop at summarizing router)

**Step-by-Step on R7:**
```bash
configure terminal
!
interface FastEthernet0/0
 ip summary-address eigrp 100 172.16.0.0 255.255.0.0
!
end
```

**Verification:**
```bash
! On R7 - Check for Null0 route
show ip route | include Null0

! On R1 - Should see single summary
show ip route 172.16.0.0
```

---

### Task 3: Configure Summarization on R3

**Objective:** Summarize the 192.168.0.0/16 networks at R3.

**Theory:**
By summarizing at R3, we prevent R2 and R1 from seeing individual /24 routes. If any 192.168.x.x network flaps, the query is contained at R3.

**Step-by-Step on R3:**
```bash
configure terminal
!
interface FastEthernet0/0
 ip summary-address eigrp 100 192.168.0.0 255.255.0.0
!
end
```

**Verification:**
```bash
! On R2 - Should see summary, not specifics
show ip route 192.168.0.0

! On R1 - Should see summary only
show ip route eigrp | include 192.168
```

---

### Task 4: Verify Query Boundaries

**Objective:** Confirm that summarization creates effective query boundaries.

**Theory:**
When a route covered by a summary goes down, EIGRP sends queries. With summarization:
- Queries stop at the summarizing router
- Other routers only know the summary (which remains valid)
- Faster convergence and reduced SIA risk

**Step-by-Step:**
```bash
! On R3 - Simulate a network failure
configure terminal
interface Loopback1
 shutdown
exit

! On R1 - Should see NO query activity
debug eigrp packets query

! Wait 10 seconds, then restore
configure terminal
interface Loopback1
 no shutdown
end

! Disable debug
undebug all
```

**Expected:** R1 should not receive any queries because R3's summary remains valid.

---

## 6. Verification & Analysis Table

| Command | Expected Output | What It Confirms |
|---------|----------------|------------------|
| `show ip route eigrp` on R1 | 172.16.0.0/16 and 192.168.0.0/16 as D routes | Summaries received |
| `show ip route | include Null0` on R7 | `172.16.0.0/16 is directly connected, Null0` | Local summary installed |
| `show ip route | include Null0` on R3 | `192.168.0.0/16 is directly connected, Null0` | Local summary installed |
| `show ip eigrp topology` on R1 | Summary routes in topology | DUAL tracks summaries |
| `ping 172.16.1.1 source 1.1.1.1` | 100% success | Reachability via summary |
| `show ip route summary` on R1 | Fewer routes than before | Table optimization |

---

## 7. Troubleshooting Challenge

### Scenario
After implementing summarization, users report they cannot reach 172.16.3.1 from R3.

### Symptoms
- `ping 172.16.3.1 source 3.3.3.3` fails
- R3 shows the route to 172.16.0.0/16 via R2
- R1 shows the route to 172.16.0.0/16 pointing to Null0!

### Root Cause
R1 has a more specific or conflicting summary installed. Check if R1 inadvertently configured summarization, creating a local Null0 route.

### Diagnostic Commands
```bash
! On R1
show ip route 172.16.0.0 longer-prefixes
show run | include summary-address
show ip eigrp topology 172.16.0.0/16
```

### Fix
If R1 has an unwanted summary:
```bash
configure terminal
interface FastEthernet0/0
 no ip summary-address eigrp 100 172.16.0.0 255.255.0.0
end
```

### Verification
```bash
ping 172.16.3.1 source 3.3.3.3
! Should succeed
```

---

## 8. Lab Completion Checklist

- [ ] R7 integrated into EIGRP AS 100
- [ ] R7 advertises 172.16.0.0/16 summary to R1
- [ ] R3 advertises 192.168.0.0/16 summary to R2
- [ ] Null0 routes present on summarizing routers
- [ ] R1's routing table shows summaries, not specifics
- [ ] Query boundary test passed (no queries on R1 for R3's networks)
- [ ] End-to-end ping from R3 to 172.16.1.1 succeeds
- [ ] Troubleshooting challenge completed
