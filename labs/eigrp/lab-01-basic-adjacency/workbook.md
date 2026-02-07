# CCNP ENCOR EIGRP Lab 01: Basic EIGRP Adjacency
**Student Workbook & Instructor Guide**

---

## 1. Concepts & Skills Covered

- Configure EIGRP autonomous system and router-id
- Understand the EIGRP neighbor discovery process (Hello packets, multicast 224.0.0.10)
- Verify neighbor relationships using `show ip eigrp neighbors`
- Implement passive interfaces to prevent unnecessary Hello traffic
- Troubleshoot common adjacency failures (AS mismatch, K-value mismatch)
- Interpret EIGRP topology and routing tables

---

## 2. Topology & Scenario

### ASCII Diagram
```
                    ┌─────────────────┐
                    │       R1        │
                    │   (Hub Router)  │
                    │  Lo0: 1.1.1.1   │
                    └───────┬─────────┘
                            │ Fa1/0
                            │ 10.0.12.1/30
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
                    └─────────────────┘
```

### Scenario Narrative
You are deploying EIGRP across a small enterprise network. The hub router (R1) connects to a branch router (R2), which in turn connects to a remote branch (R3). Your goal is to establish full EIGRP adjacency using AS 100, optimize Hello traffic with passive interfaces, and verify end-to-end reachability.

### Device Role Table
| Device | Role | Platform | Loopback0 | EIGRP AS |
|--------|------|----------|-----------|----------|
| R1 | Hub Router | c7200 | 1.1.1.1/32 | 100 |
| R2 | Branch Router | c3725 | 2.2.2.2/32 | 100 |
| R3 | Remote Branch | c3725 | 3.3.3.3/32 | 100 |

---

## 3. Hardware & Environment Specifications

### Router Platform Table
| Device | Model | RAM | Image Name |
|--------|-------|-----|------------|
| R1 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |
| R2 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R3 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |

### Interface Slot Configuration
| Device | Slot 0 | Slot 1 | Slot 3 |
|--------|--------|--------|--------|
| R1 (c7200) | Fa0/0 | Fa1/0, Fa1/1 | Gi3/0 |
| R2 (c3725) | Fa0/0, Fa0/1 | - | - |
| R3 (c3725) | Fa0/0, Fa0/1 | - | - |

### Console Access Table
| Device | Port | Connection Command |
|--------|------|--------------------|
| R1 | 5001 | `telnet localhost 5001` |
| R2 | 5002 | `telnet localhost 5002` |
| R3 | 5003 | `telnet localhost 5003` |

### Cabling Table
| Link ID | Source:Interface | Target:Interface | Subnet |
|---------|------------------|------------------|--------|
| L1 | R1:Fa1/0 | R2:Fa0/0 | 10.0.12.0/30 |
| L2 | R2:Fa0/1 | R3:Fa0/0 | 10.0.23.0/30 |

---

## 4. Base Configuration

> ⚠️ **Apply these configurations BEFORE starting EIGRP tasks**

### R1 (Hub Router)
```bash
enable
configure terminal
!
hostname R1
!
interface Loopback0
 ip address 1.1.1.1 255.255.255.255
 no shutdown
!
interface FastEthernet1/0
 description Link to R2
 ip address 10.0.12.1 255.255.255.252
 no shutdown
!
line con 0
 logging synchronous
 exec-timeout 0 0
!
end
write memory
```

### R2 (Branch Router)
```bash
enable
configure terminal
!
hostname R2
!
interface Loopback0
 ip address 2.2.2.2 255.255.255.255
 no shutdown
!
interface FastEthernet0/0
 description Link to R1
 ip address 10.0.12.2 255.255.255.252
 no shutdown
!
interface FastEthernet0/1
 description Link to R3
 ip address 10.0.23.1 255.255.255.252
 no shutdown
!
line con 0
 logging synchronous
 exec-timeout 0 0
!
end
write memory
```

### R3 (Remote Branch)
```bash
enable
configure terminal
!
hostname R3
!
interface Loopback0
 ip address 3.3.3.3 255.255.255.255
 no shutdown
!
interface FastEthernet0/0
 description Link to R2
 ip address 10.0.23.2 255.255.255.252
 no shutdown
!
line con 0
 logging synchronous
 exec-timeout 0 0
!
end
write memory
```

### Pre-Lab Verification
Run these commands to confirm Layer 3 connectivity before starting EIGRP:
```bash
! From R1:
ping 10.0.12.2

! From R2:
ping 10.0.12.1
ping 10.0.23.2

! From R3:
ping 10.0.23.1
```

---

## 5. Configuration Tasks Workbook

### Task 1: Enable EIGRP and Advertise Networks

**Objective:** Configure EIGRP AS 100 on all routers and advertise all connected networks.

**Theory:**
EIGRP uses Hello packets (multicast 224.0.0.10) to discover neighbors. For adjacency to form, routers must have:
- Matching AS number
- Matching K-values (bandwidth, delay, reliability, load, MTU weights)
- Interfaces in the same subnet
- Authentication (if configured)

**Step-by-Step:**

**On R1:**
```bash
configure terminal
!
router eigrp 100
 eigrp router-id 1.1.1.1
 network 1.1.1.1 0.0.0.0
 network 10.0.12.0 0.0.0.3
 no auto-summary
!
end
```

**On R2:**
```bash
configure terminal
!
router eigrp 100
 eigrp router-id 2.2.2.2
 network 2.2.2.2 0.0.0.0
 network 10.0.12.0 0.0.0.3
 network 10.0.23.0 0.0.0.3
 no auto-summary
!
end
```

**On R3:**
```bash
configure terminal
!
router eigrp 100
 eigrp router-id 3.3.3.3
 network 3.3.3.3 0.0.0.0
 network 10.0.23.0 0.0.0.3
 no auto-summary
!
end
```

---

### Task 2: Configure Passive Interfaces

**Objective:** Prevent EIGRP Hello packets from being sent on Loopback interfaces.

**Theory:**
Passive interfaces suppress Hello packets on interfaces where no neighbors are expected. This:
- Reduces CPU overhead
- Prevents accidental adjacency formation
- Is best practice for Loopbacks and management interfaces

**Step-by-Step (All Routers):**
```bash
configure terminal
!
router eigrp 100
 passive-interface Loopback0
!
end
```

---

### Task 3: Verify EIGRP Adjacencies

**Objective:** Confirm all routers have established neighbor relationships.

**Theory:**
The `show ip eigrp neighbors` command displays:
- **H**: Handle number (order neighbor was discovered)
- **Address**: Neighbor's IP address
- **Interface**: Local interface facing the neighbor
- **Hold**: Time before declaring neighbor dead (default 15 sec)
- **Uptime**: Duration since adjacency formed
- **SRTT**: Smooth Round Trip Time (in ms)
- **Q Cnt**: Packets in queue waiting to be sent

**Verification Commands:**
```bash
show ip eigrp neighbors
show ip eigrp interfaces
show ip protocols
```

---

## 6. Verification & Analysis Table

| Command | Expected Output | What It Confirms |
|---------|----------------|------------------|
| `show ip eigrp neighbors` | R1 shows 1 neighbor (R2), R2 shows 2 neighbors | Adjacencies are UP |
| `show ip eigrp interfaces` | Fa1/0 (R1), Fa0/0+Fa0/1 (R2), Fa0/0 (R3) listed | EIGRP enabled on correct interfaces |
| `show ip eigrp interfaces` | Loopback0 NOT listed | Passive interface working |
| `show ip route eigrp` | R1 sees 2.2.2.2/32 and 3.3.3.3/32 | Routes learned via EIGRP |
| `ping 3.3.3.3 source 1.1.1.1` | 100% success | End-to-end reachability confirmed |
| `show ip protocols` | Shows EIGRP 100, networks advertised | Protocol configuration correct |

---

## 7. Troubleshooting Challenge

### Scenario
After completing all tasks, a network administrator accidentally changes R2's EIGRP AS number to 200. What happens?

### Symptoms
- R1 loses neighbor relationship with R2
- R3 loses neighbor relationship with R2
- `show ip eigrp neighbors` on R1 shows empty table
- Routes to 2.2.2.2, 3.3.3.3, and 10.0.23.0/30 disappear from R1

### Diagnostic Commands
```bash
! On R1:
show ip eigrp neighbors
show ip eigrp interfaces
debug eigrp packets hello
```

### Root Cause
EIGRP AS number mismatch. R1 and R3 are in AS 100, but R2 is now in AS 200. EIGRP requires matching AS numbers for adjacency.

### Fix
```bash
! On R2:
configure terminal
no router eigrp 200
!
router eigrp 100
 eigrp router-id 2.2.2.2
 network 2.2.2.2 0.0.0.0
 network 10.0.12.0 0.0.0.3
 network 10.0.23.0 0.0.0.3
 no auto-summary
 passive-interface Loopback0
!
end
```

### Verification of Fix
```bash
show ip eigrp neighbors
! Should show neighbors on both Fa0/0 and Fa0/1

ping 1.1.1.1 source 3.3.3.3
! Should succeed
```

---

## 8. Lab Completion Checklist

- [ ] All three routers have EIGRP AS 100 configured
- [ ] Router-IDs are set to Loopback0 addresses
- [ ] All physical and loopback networks are advertised
- [ ] Loopback0 is configured as passive on all routers
- [ ] `show ip eigrp neighbors` shows expected neighbors
- [ ] End-to-end ping from R1 to R3's loopback succeeds
- [ ] Troubleshooting challenge completed successfully
