# CCNP ENCOR EIGRP Lab 02: Path Selection & Metrics
**Student Workbook & Instructor Guide**

---

## 1. Concepts & Skills Covered

- Understand EIGRP composite metric calculation (Bandwidth + Delay)
- Analyze the DUAL algorithm and Feasibility Condition
- Identify Successor and Feasible Successor routes
- Manipulate path selection using interface delay
- Configure variance for unequal-cost load balancing
- Interpret EIGRP topology table entries

---

## 2. Topology & Scenario

### ASCII Diagram
```
                    ┌─────────────────┐
                    │       R1        │
                    │   (Hub Router)  │
                    │  Lo0: 1.1.1.1   │
                    └───┬─────────┬───┘
                        │ Fa1/0   │ Fa1/1 (NEW)
                        │         │
          10.0.12.1/30  │         │ 10.0.13.1/30
                        │         │
                        │         │ 10.0.13.2/30
                ┌───────┴─────┐   │ Fa0/1
                │      R2     │   │
                │   Branch    │   │
                │  2.2.2.2    │   │
                └───────┬─────┴───┘
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
Your EIGRP network now has redundancy. A new direct link (L7) has been established between R1 and R3, creating two possible paths to reach R3's loopback:
1. **Direct path**: R1 → R3 (1 hop)
2. **Indirect path**: R1 → R2 → R3 (2 hops)

By default, EIGRP will prefer the direct path due to lower composite metric. In this lab, you will manipulate metrics to influence path selection and then enable unequal-cost load balancing using variance.

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

### Console Access Table
| Device | Port | Connection Command |
|--------|------|--------------------|
| R1 | 5001 | `telnet localhost 5001` |
| R2 | 5002 | `telnet localhost 5002` |
| R3 | 5003 | `telnet localhost 5003` |

### Cabling Table
| Link ID | Source:Interface | Target:Interface | Subnet | Status |
|---------|------------------|------------------|--------|--------|
| L1 | R1:Fa1/0 | R2:Fa0/0 | 10.0.12.0/30 | Existing |
| L2 | R2:Fa0/1 | R3:Fa0/0 | 10.0.23.0/30 | Existing |
| L7 | R1:Fa1/1 | R3:Fa0/1 | 10.0.13.0/30 | **NEW** |

---

## 4. Base Configuration

> ⚠️ **This lab builds on Lab 01**. Initial configs include EIGRP AS 100 on existing links.

### R1 (Add New Link)
```bash
enable
configure terminal
!
interface FastEthernet1/1
 description Redundant Link to R3
 ip address 10.0.13.1 255.255.255.252
 no shutdown
!
router eigrp 100
 network 10.0.13.0 0.0.0.3
!
end
write memory
```

### R3 (Add New Link)
```bash
enable
configure terminal
!
interface FastEthernet0/1
 description Redundant Link to R1
 ip address 10.0.13.2 255.255.255.252
 no shutdown
!
router eigrp 100
 network 10.0.13.0 0.0.0.3
!
end
write memory
```

### Pre-Task Verification
```bash
! On R1:
show ip eigrp neighbors
! Should now show 2 neighbors: R2 (10.0.12.2) and R3 (10.0.13.2)

ping 10.0.13.2
! Should succeed
```

---

## 5. Configuration Tasks Workbook

### Task 1: Analyze Default Path Selection

**Objective:** Understand which path EIGRP selects by default and why.

**Theory:**
EIGRP uses a composite metric formula:
```
Metric = 256 × [(10^7 / minimum_bandwidth_kbps) + (cumulative_delay_tens_of_microseconds)]
```

By default (K1=1, K3=1, K2=0, K4=0, K5=0), only **bandwidth** and **delay** matter.

The path with the **lowest metric** becomes the **Successor** and is installed in the routing table.

**Step-by-Step:**

**On R1:**
```bash
show ip route 3.3.3.3
```

**Expected Output:**
```
D       3.3.3.3 [90/XXXXXX] via 10.0.13.2, 00:XX:XX, FastEthernet1/1
```

The direct link (Fa1/1) is preferred because it has fewer hops and thus lower cumulative delay.

**Examine the topology table:**
```bash
show ip eigrp topology 3.3.3.3/32
```

**Expected Output:**
```
P 3.3.3.3/32, 1 successors, FD is XXXXXX
        via 10.0.13.2 (XXXXXX/YYYYYY), FastEthernet1/1
        via 10.0.12.2 (ZZZZZZ/WWWWWW), FastEthernet1/0
```

- First line: Successor (best path)
- Second line: Feasible Successor (backup path, if FC is met)

---

### Task 2: Manipulate Metrics Using Delay

**Objective:** Make the indirect path (via R2) the Successor by increasing delay on the direct link.

**Theory:**
Modifying **delay** is preferred over bandwidth because:
- Bandwidth affects QoS and other protocols
- Delay is purely for routing metric calculation
- Delay is cumulative across the path

**Step-by-Step:**

**On R1:**
```bash
configure terminal
!
interface FastEthernet1/1
 delay 5000
 ! Default delay is typically 100 (1000 microseconds)
 ! Setting to 5000 = 50,000 microseconds = 50ms
!
end
```

**Verification:**
```bash
show ip route 3.3.3.3
```

**Expected Output:**
```
D       3.3.3.3 [90/XXXXXX] via 10.0.12.2, 00:XX:XX, FastEthernet1/0
```

Now the path through R2 should be the Successor.

**Examine the topology table again:**
```bash
show ip eigrp topology 3.3.3.3/32
```

Verify that:
- The path via 10.0.12.2 (R2) is now the Successor
- The path via 10.0.13.2 (R3 direct) is now listed second

---

### Task 3: Verify the Feasibility Condition

**Objective:** Confirm that the direct link qualifies as a Feasible Successor.

**Theory:**
The **Feasibility Condition** ensures loop-free backup paths:

**Feasibility Condition:** `Reported Distance (RD) < Feasible Distance (FD)`

Where:
- **RD (Reported Distance)**: The metric advertised by the neighbor
- **FD (Feasible Distance)**: The best metric to reach the destination

If a neighbor's RD is less than the current Successor's FD, that neighbor can be a **Feasible Successor** and will be used immediately if the Successor fails (no Query process needed).

**Step-by-Step:**

**On R1:**
```bash
show ip eigrp topology all-links
```

Look for the entry for 3.3.3.3/32. You should see both paths listed.

**Example Output:**
```
P 3.3.3.3/32, 1 successors, FD is 156160
        via 10.0.12.2 (156160/128256), FastEthernet1/0
        via 10.0.13.2 (2816/256), FastEthernet1/1
```

In this example:
- Successor: via 10.0.12.2, FD = 156160
- The path via 10.0.13.2 has RD = 256
- Since 256 < 156160, it **meets the Feasibility Condition**
- Therefore, 10.0.13.2 is a **Feasible Successor**

---

### Task 4: Configure Unequal-Cost Load Balancing

**Objective:** Use the `variance` command to enable load balancing across both paths.

**Theory:**
EIGRP is the only IGP that supports **unequal-cost load balancing**.

The `variance` multiplier allows routes with metrics up to `variance × FD` to be installed in the routing table, **provided they meet the Feasibility Condition**.

Formula: `Route is installed if: Route_Metric ≤ (Variance × Successor_FD) AND FC is met`

**Step-by-Step:**

1. **Calculate the required variance:**
   - If Successor FD = 156160
   - If FS metric = 2816
   - Variance needed = 1 (since 2816 < 156160, variance 1 is sufficient)
   - However, to demonstrate, we'll use variance 2

2. **Configure variance:**

**On R1:**
```bash
configure terminal
!
router eigrp 100
 variance 2
!
end
```

**Verification:**
```bash
show ip route 3.3.3.3
```

**Expected Output:**
```
D       3.3.3.3 [90/156160] via 10.0.12.2, 00:XX:XX, FastEthernet1/0
                [90/2816] via 10.0.13.2, 00:XX:XX, FastEthernet1/1
```

You should now see **two** routes to 3.3.3.3 with different metrics. Traffic will be load-balanced proportionally based on the metrics (inverse ratio).

**Additional Verification:**
```bash
show ip protocols
```

Look for the line showing variance:
```
EIGRP-IPv4 Protocol for AS(100)
  ...
  Variance metric: 2
```

---

## 6. Verification & Analysis Table

| Command | Expected Output | What It Confirms |
|---------|----------------|------------------|
| `show ip eigrp neighbors` | 2 neighbors on R1 (R2 and R3) | Adjacencies formed on both links |
| `show ip eigrp topology 3.3.3.3/32` | Two paths listed | DUAL knows multiple paths |
| `show ip route 3.3.3.3` | Two next-hops after variance | Unequal-cost load balancing active |
| `show ip eigrp topology all-links` | Feasibility Condition verified | Backup path is loop-free |
| `show interfaces Fa1/1` | Delay 50000 usec | Metric manipulation applied |

---

## 7. Troubleshooting Challenge

### Scenario
After configuring `variance 10`, you notice that R1 still only uses one path to reach 3.3.3.3.

### Symptoms
- `show ip route 3.3.3.3` shows only one next-hop
- `show ip eigrp topology all-links` shows the second path exists
- The second path is NOT marked as a Feasible Successor

### Diagnostic Commands
```bash
show ip eigrp topology 3.3.3.3/32
show ip eigrp topology all-links
```

### Root Cause
The **Feasibility Condition is not met**. Even with a high variance, EIGRP will not use a path if:

`Neighbor's RD ≥ Current Successor's FD`

This violates the loop-free guarantee. The path may be available but cannot be used for load balancing.

### Solution
Adjust the delay on intermediate links to ensure the neighbor's advertised distance (RD) is lower than the Successor's FD. For example:

**On R2:**
```bash
configure terminal
interface FastEthernet0/1
 delay 100
!
end
```

This reduces the cumulative delay through R2, lowering the RD reported to R1.

### Verification of Fix
```bash
show ip eigrp topology 3.3.3.3/32
```

Verify that the path now meets the Feasibility Condition and appears in the routing table.

---

## 8. Lab Completion Checklist

- [ ] New link L7 configured between R1 and R3
- [ ] EIGRP adjacency formed on all three links
- [ ] Default path selection analyzed and understood
- [ ] Delay modified on Fa1/1 to influence path selection
- [ ] Feasibility Condition verified for backup path
- [ ] Variance configured to enable unequal-cost load balancing
- [ ] Two routes to 3.3.3.3 visible in routing table
- [ ] Troubleshooting challenge completed
