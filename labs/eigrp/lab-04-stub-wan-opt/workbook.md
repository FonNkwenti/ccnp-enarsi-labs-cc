# CCNP ENCOR EIGRP Lab 04: Stub & WAN Optimization
**Student Workbook & Instructor Guide**

---

## 1. Concepts & Skills Covered

- Configure EIGRP stub routers to reduce query traffic
- Understand stub router types (connected, static, summary, redistributed, receive-only)
- Adjust interface bandwidth for accurate metric calculation
- Tune EIGRP hello and hold timers for WAN links
- Verify stub configuration and query boundary effects
- Optimize EIGRP for WAN environments

---

## 2. Topology & Scenario

### ASCII Diagram
```
                    ┌─────────────────┐
                    │       R1        │
                    │   (Hub Router)  │
                    │  Lo0: 1.1.1.1   │
                    └───┬─────────┬───┘
                        │ Fa1/0   │ Fa1/1 (WAN Link)
                        │         │ 10.0.12.1/30
                        │         │ BW: 1544 Kbps
           10.0.12.1/30 │         │ Hello: 60, Hold: 180
                        │         │
                        │         │ 10.0.12.2/30
                        │    ┌────┴────────┐
                        │    │     R2      │
                        │    │   Branch    │
                        │    │ 2.2.2.2/32  │
                        │    └────┬────────┘
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
```

### Scenario Narrative
Your enterprise network includes a remote stub site (R5) that only needs to advertise its local networks and receive a default route. To optimize network stability and reduce unnecessary EIGRP query traffic, you need to:

1. **Configure R5 as an EIGRP stub router** - This prevents R5 from being queried during topology changes, reducing convergence time and SIA (Stuck-In-Active) risks.

2. **Adjust WAN link bandwidth** - The link between R1 and R2 represents a T1 WAN connection (1.544 Mbps). You must configure the correct bandwidth to ensure accurate metric calculation and proper path selection.

3. **Tune EIGRP timers** - WAN links with higher latency require longer hello and hold timers to prevent false neighbor loss. Configure appropriate timer values for the WAN link.

### Device Role Table
| Device | Role | Platform | Loopback0 | New in Lab 04 |
|--------|------|----------|-----------|---------------|
| R1 | Hub Router | c7200 | 1.1.1.1/32 | No |
| R2 | Branch Router | c3725 | 2.2.2.2/32 | No |
| R3 | Remote Branch | c3725 | 3.3.3.3/32 | No |
| R5 | Stub Network | c3725 | 5.5.5.5/32 | **Yes** |

---

## 3. Hardware & Environment Specifications

### Router Platform Table
| Device | Model | RAM | Image Name |
|--------|-------|-----|------------|
| R1 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |
| R2 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R3 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R5 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |

### Console Access Table
| Device | Port | Connection Command |
|--------|------|--------------------|
| R1 | 5001 | `telnet localhost 5001` |
| R2 | 5002 | `telnet localhost 5002` |
| R3 | 5003 | `telnet localhost 5003` |
| R5 | 5005 | `telnet localhost 5005` |

### Cabling Table
| Link ID | Source:Interface | Target:Interface | Subnet | Status |
|---------|------------------|------------------|--------|--------|
| L1 | R1:Fa1/0 | R2:Fa0/0 | 10.0.12.0/30 | Existing (WAN) |
| L2 | R2:Fa0/1 | R3:Fa0/0 | 10.0.23.0/30 | Existing |
| L4 | R3:Fa0/1 | R5:Fa0/0 | 10.0.35.0/30 | **New** |

---

## 4. Base Configuration

> ⚠️ **This lab builds on Lab 03.** Initial configs include EIGRP from previous labs.

### R1 and R2 (Existing Configuration)
R1 and R2 already have EIGRP adjacency established via FastEthernet1/0 (R1) and FastEthernet0/0 (R2) using subnet 10.0.12.0/30. No additional configuration is required at this stage.

### R5 (New Device - Complete Config)
```bash
enable
configure terminal
!
hostname R5
!
! Loopback interfaces for stub networks
interface Loopback0
 ip address 5.5.5.5 255.255.255.255
 no shutdown
!
interface Loopback1
 ip address 10.5.1.1 255.255.255.0
 no shutdown
!
interface Loopback2
 ip address 10.5.2.1 255.255.255.0
 no shutdown
!
interface Loopback3
 ip address 10.5.3.1 255.255.255.0
 no shutdown
!
! Connection to R3
interface FastEthernet0/0
 description Link to R3 (Remote Branch)
 ip address 10.0.35.2 255.255.255.252
 no shutdown
!
! EIGRP configuration - will be modified to stub in Task 1
router eigrp 100
 eigrp router-id 5.5.5.5
 network 5.5.5.5 0.0.0.0
 network 10.0.35.0 0.0.0.3
 network 10.5.0.0 0.0.255.255
 no auto-summary
 passive-interface Loopback0
 passive-interface Loopback1
 passive-interface Loopback2
 passive-interface Loopback3
!
line con 0
 logging synchronous
 exec-timeout 0 0
!
end
write memory
```

### R3 (Add Connection to R5)
```bash
enable
configure terminal
!
interface FastEthernet0/1
 description Link to R5 (Stub Network)
 ip address 10.0.35.1 255.255.255.252
 no shutdown
!
router eigrp 100
 network 10.0.35.0 0.0.0.3
!
end
write memory
```

---

### Pre-Task Verification
After applying the base configuration, verify connectivity:
```bash
! On R3:
ping 10.0.35.2
! Should succeed

! On R5:
ping 10.0.35.1
! Should succeed

! Check EIGRP adjacencies:
show ip eigrp neighbors
! Should show R3 as neighbor on R5, and vice versa
```

## 5. Configuration Tasks Workbook

### Task 1: Configure R5 as EIGRP Stub Router

**Objective:** Configure R5 as an EIGRP stub router to reduce query traffic and improve network stability.

**Theory:**
EIGRP stub routers:
- Advertise only connected, summary, static, or redistributed routes (depending on stub type)
- Do NOT advertise learned EIGRP routes to neighbors
- Are NOT queried for lost routes (query boundary)
- Receive a default route from neighbors (optional)

**Step-by-Step on R5:**
```bash
configure terminal
!
router eigrp 100
 eigrp stub connected summary
 ! Options: connected, static, summary, redistributed, receive-only
!
end
```

**Verification:**
```bash
! On R5 - Verify stub configuration
show ip protocols | include stub
! Expected: "EIGRP stub, connected, summary"

! On R3 - Verify neighbor shows as stub
show ip eigrp neighbors detail
! Look for: "Stub Peer Advertising (CONNECTED SUMMARY) Routes"

! On R1 - Check routes from R5
show ip route eigrp | include 10.5
! Should see routes: 10.5.1.0/24, 10.5.2.0/24, 10.5.3.0/24
```

---

### Task 2: Verify Stub Router Behavior

**Objective:** Confirm that stub configuration reduces query traffic and creates proper query boundaries.

**Theory:**
When a route fails elsewhere in the network, EIGRP sends queries to find alternate paths. Stub routers are excluded from this query process, which:
- Reduces convergence time
- Prevents SIA (Stuck-In-Active) conditions
- Limits query scope

**Step-by-Step:**
1. **Simulate a network failure:**
```bash
! On R1 - Shutdown an interface with advertised networks
configure terminal
interface Loopback1
 shutdown
exit
```

2. **Monitor query activity:**
```bash
! On R3 - Enable debug to see queries
debug eigrp packets query
! Wait 10 seconds

! On R5 - Check if any queries received
debug eigrp packets query
! Should see NO queries (stub routers are not queried)

! Disable debug
undebug all

! Restore the interface
configure terminal
interface Loopback1
 no shutdown
end
```

**Expected Result:** R5 (stub router) should not receive any queries for the lost route.

---

### Task 3: Adjust WAN Link Bandwidth

**Objective:** Configure accurate bandwidth on WAN links for proper metric calculation.

**Theory:**
EIGRP metric calculation uses bandwidth as a primary component:
- Default bandwidth values may not reflect actual WAN capacity
- Incorrect bandwidth leads to suboptimal path selection
- Bandwidth command affects QoS and other protocols

**Step-by-Step on R1 and R2:**

**On R1:**
```bash
configure terminal
interface FastEthernet1/0
 bandwidth 1544
 exit
!
! Verify bandwidth configuration
show interface FastEthernet1/0 | include BW
! Expected: "BW 1544 Kbit"
```

**On R2:**
```bash
configure terminal
interface FastEthernet0/0
 bandwidth 1544
 exit
!
! Verify bandwidth configuration
show interface FastEthernet0/0 | include BW
! Expected: "BW 1544 Kbit"
```

**Calculate metric impact (on either router):**
```bash
show ip eigrp topology 3.3.3.3/32
! Note the metric value - compare with default 100 Mbps bandwidth
```

**Verification:**

**On R1:**
```bash
! Check bandwidth setting
show interface FastEthernet1/0 | include BW
! Should show: BW 1544 Kbit
```

**On R2:**
```bash
! Check bandwidth setting
show interface FastEthernet0/0 | include BW
! Should show: BW 1544 Kbit
```

**Verify metric calculation (on either router):**
```bash
show ip eigrp topology 3.3.3.3/32
! Compare metric with default 100 Mbps bandwidth
```

---

### Task 4: Tune EIGRP Hello and Hold Timers

**Objective:** Adjust EIGRP timers for WAN links with higher latency.

**Theory:**
- **Hello interval:** How often hello packets are sent (default: 5 seconds on high BW, 60 seconds on low BW)
- **Hold time:** How long to wait without hearing a hello before declaring neighbor down (default: 3x hello)
- WAN links may need longer timers to prevent false neighbor loss

**Step-by-Step on R1 and R2:**

**On R1:**
```bash
configure terminal
interface FastEthernet1/0
 ip hello-interval eigrp 100 60
 ip hold-time eigrp 100 180
 exit
!
! Verify timer configuration
show ip eigrp interfaces detail FastEthernet1/0
! Look for: Hello interval 60 sec, Hold time 180 sec
```

**On R2:**
```bash
configure terminal
interface FastEthernet0/0
 ip hello-interval eigrp 100 60
 ip hold-time eigrp 100 180
 exit
!
! Verify timer configuration
show ip eigrp interfaces detail FastEthernet0/0
! Look for: Hello interval 60 sec, Hold time 180 sec
```

**Verification:**

**On R1:**
```bash
! Check timer configuration
show ip eigrp interfaces detail FastEthernet1/0 | include Hello|Hold
! Expected: "Hello interval is 60 seconds", "Hold time is 180 seconds"
```

**On R2:**
```bash
! Check timer configuration
show ip eigrp interfaces detail FastEthernet0/0 | include Hello|Hold
! Expected: "Hello interval is 60 seconds", "Hold time is 180 seconds"
```

**Verify neighbor relationship (on either router):**
```bash
show ip eigrp neighbors
! Neighbor should be in UP state
```

---

### Task 5: Configure Receive-Only Stub (Optional Advanced Task)

**Objective:** Configure R5 as a receive-only stub that only receives a default route.

**Theory:**
Receive-only stub routers:
- Do NOT advertise any routes (not even connected)
- Only receive a default route from neighbors
- Useful for pure leaf nodes

**Step-by-Step on R5:**
```bash
configure terminal
!
router eigrp 100
 no eigrp stub connected summary
 eigrp stub receive-only
!
end
```

**Verification:**
```bash
! On R5 - Check routing table
show ip route eigrp
! Should only see default route (0.0.0.0/0)

! On R3 - Check advertised routes
show ip eigrp neighbors detail
! Should see: "Stub Peer Advertising (RECEIVE-ONLY) Routes"

! Restore to previous stub configuration
configure terminal
router eigrp 100
 no eigrp stub receive-only
 eigrp stub connected summary
end
```

---

## 6. Verification & Analysis Table

| Command | Expected Output | What It Confirms |
|---------|----------------|------------------|
| `show ip protocols \| include stub` on R5 | "EIGRP stub, connected, summary" | Stub configuration active |
| `show ip eigrp neighbors detail` on R3 | "Stub Peer Advertising (CONNECTED SUMMARY) Routes" | Neighbor recognizes stub |
| `show interface Fa1/0 \| include BW` on R1 | "BW 1544 Kbit" | WAN bandwidth configured |
| `show ip eigrp interfaces detail Fa1/0` on R1 | "Hello interval is 60 seconds", "Hold time is 180 seconds" | Timer adjustment applied |
| `show ip route eigrp \| include 10.5` on R1 | Routes for 10.5.1.0/24, 10.5.2.0/24, 10.5.3.0/24 | Stub routes received |
| `debug eigrp packets query` on R5 during failure | No query packets received | Query boundary effective |
| `ping 10.5.1.1 source 1.1.1.1` | 100% success | End-to-end reachability |

---

## 7. Troubleshooting Challenge

### Scenario
After configuring R5 as a stub router, R1 cannot reach the 10.5.0.0/16 networks behind R5.

### Symptoms
- `ping 10.5.1.1 source 1.1.1.1` fails
- R3 shows R5 as a neighbor in UP state
- R1's routing table shows no routes to 10.5.0.0/16
- R5's routing table shows routes to all other networks

### Diagnostic Commands
```bash
! On R5
show ip protocols
show ip eigrp neighbors

! On R3
show ip eigrp neighbors detail
show ip route 10.5.0.0

! On R1
show ip route eigrp
```

### Root Cause
Possible causes:
1. R5's stub configuration missing or incorrect
2. Network statements missing on R5
3. Route filtering on R3
4. Passive interface misconfiguration

### Fix
Check and correct R5's EIGRP configuration:
```bash
! On R5
configure terminal
router eigrp 100
 eigrp stub connected summary
 network 10.5.0.0 0.0.255.255
 no passive-interface FastEthernet0/0
!
end
```

### Verification
```bash
ping 10.5.1.1 source 1.1.1.1
! Should succeed
```

---

## 8. Lab Completion Checklist

- [ ] R5 integrated into EIGRP AS 100
- [ ] R5 configured as EIGRP stub (connected, summary)
- [ ] WAN link bandwidth adjusted to 1544 Kbps on R1 and R2
- [ ] Hello interval set to 60 seconds, hold time to 180 seconds on WAN link
- [ ] Stub configuration verified on both R5 and R3
- [ ] Query boundary test passed (no queries sent to R5)
- [ ] End-to-end reachability verified (ping from R1 to 10.5.1.1)
- [ ] Optional receive-only stub configuration tested
- [ ] Troubleshooting challenge completed
