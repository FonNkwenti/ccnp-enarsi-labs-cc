# CCNP ENCOR EIGRP Lab 07: Redistribution
**Student Workbook & Instructor Guide**

---

## 1. Concepts & Skills Covered

- Configure mutual redistribution between EIGRP and OSPF
- Understand seed metrics for different routing protocols
- Prevent routing loops using route tags and filtering
- Manipulate metrics for redistributed routes to influence path selection
- Verify redistribution using routing tables and topology databases
- Troubleshoot common redistribution issues (metric mismatch, reachability)

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
                    │   (Hub Router)  │
                    │  Lo0: 1.1.1.1   │
                    └───┬─────────┬───┘
                        │ Fa1/0   │ Fa1/1 (WAN Link)
                        │         │ 10.0.12.1/30
                        │         │
           10.0.12.1/30 │         │
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
**Skynet Global** has recently acquired a smaller tech firm, **CyberDyne Systems**, which utilizes **OSPF** as its primary internal gateway protocol. As the Lead Network Architect, you must integrate CyberDyne's infrastructure into the Skynet EIGRP domain.

The CyberDyne router (**R4**) is connected to the Skynet Hub (**R1**). Your objective is to perform **mutual redistribution** between the two protocols to ensure full reachability across the merged enterprise. You must be cautious to prevent routing loops and ensure that metrics are correctly translated so that traffic flows through the most efficient paths.

### Device Role Table
| Device | Role | Platform | Loopback0 | New in Lab 07 |
|--------|------|----------|-----------|---------------|
| R1 | Hub Router / ASBR | c7200 | 1.1.1.1/32 | No |
| R2 | Branch Router | c3725 | 2.2.2.2/32 | No |
| R3 | Remote Branch | c3725 | 3.3.3.3/32 | No |
| R4 | CyberDyne OSPF Router | c3725 | 4.4.4.4/32 | **Yes** |
| R5 | Stub Network | c3725 | 5.5.5.5/32 | No |

---

## 3. Hardware & Environment Specifications

### Router Platform Table
| Device | Model | RAM | Image Name |
|--------|-------|-----|------------|
| R1 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |
| R2 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R3 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R4 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R5 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |

---

## 4. Base Configuration

> ⚠️ **This lab builds on Lab 06.** Ensure that all previous security and filtering configurations are verified before proceeding with redistribution.

### R4 (CyberDyne - Integration)
```bash
enable
configure terminal
hostname R4
interface Loopback0
 ip address 4.4.4.4 255.255.255.255
interface FastEthernet0/0
 ip address 10.0.14.2 255.255.255.252
 no shutdown
router ospf 1
 network 4.4.4.4 0.0.0.0 area 0
 network 10.0.14.0 0.0.0.3 area 0
end
```

### R1 (Link to CyberDyne)
```bash
interface FastEthernet1/1
 description Link to CyberDyne (OSPF Domain)
 ip address 10.0.14.1 255.255.255.252
 no shutdown
router ospf 1
 network 10.0.14.0 0.0.0.3 area 0
end
```

---

## 5. Lab Challenge: Protocol Redistribution & Loop Prevention

### Objective 1: Implement Mutual Redistribution (R1)
Perform mutual redistribution between EIGRP AS 100 and OSPF process 1 on the Hub router.
- Redistribute **EIGRP** into **OSPF**. Use a metric of `100` and ensure the metric-type is **E1**.
- Redistribute **OSPF** into **EIGRP**. Use the standard EIGRP K-values: Bandwidth `10000`, Delay `100`, Reliability `255`, Load `1`, MTU `1500`.

### Objective 2: Loop Prevention using Route Tagging
To prevent potential routing loops during future expansions:
- When redistributing routes into EIGRP on **R1**, tag them with tag `111`.
- When redistributing routes into OSPF on **R1**, tag them with tag `222`.
- Configure a route-map to deny the re-importation of routes already tagged with `111` or `222`.

### Objective 3: Verify Reachability
- Verify that **R4** (CyberDyne) can ping the Skynet Branch loopbacks (**2.2.2.2**, **3.3.3.3**).
- Verify that **R5** (Stub) can reach the CyberDyne loopback (**4.4.4.4**) (assuming previous filters allow it).

---

## 6. Verification & Analysis

| Command | Expected Outcome |
|---------|------------------|
| `show ip route ospf` | On R4, confirm Skynet EIGRP routes are present as OSPF E1 routes. |
| `show ip route eigrp` | On R2/R3, confirm CyberDyne OSPF routes are present as EIGRP External routes (EX). |
| `show ip eigrp topology <network>` | Verify that external routes have the correct tag `111`. |
| `show ip ospf database external` | Verify that external LSAs have the correct tag `222`. |

---

## 7. Verification Cheatsheet

### 7.1 Verify OSPF External Routes (R4)
```bash
R4# show ip route ospf
...
O E1  2.2.2.2 [110/120] via 10.0.14.1, 00:05:12, FastEthernet0/0
O E1  3.3.3.3 [110/120] via 10.0.14.1, 00:05:12, FastEthernet0/0
```

### 7.2 Verify EIGRP External Routes (R2)
```bash
R2# show ip route eigrp
...
D EX  4.4.4.4 [170/2560512] via 10.0.12.1, 00:04:45, FastEthernet0/0
```

---

## 8. Troubleshooting Scenario

### The Fault
After configuring redistribution, R4 can see Skynet routes, but R2 cannot see the 4.4.4.4 loopback from CyberDyne.

### The Mission
1. Check if redistribution is active on R1 under the `router eigrp 100` process.
2. Verify if a seed metric was provided for OSPF-to-EIGRP redistribution. (Remember: EIGRP has an infinite default metric for external routes!)
3. Restore reachability and confirm the routes appear as `D EX` on R2.

---

## 9. Solutions (Spoiler Alert!)

### Objective 1 & 2: Mutual Redistribution & Tagging (R1)
```bash
route-map EIGRP_TO_OSPF permit 10
 set tag 222
 set metric 100
 set metric-type type-1
!
route-map OSPF_TO_EIGRP permit 10
 set tag 111
!
router eigrp 100
 redistribute ospf 1 metric 10000 100 255 1 1500 route-map OSPF_TO_EIGRP
!
router ospf 1
 redistribute eigrp 100 route-map EIGRP_TO_OSPF subnets
```

---

## 10. Lab Completion Checklist

- [ ] Mutual redistribution functional on R1.
- [ ] OSPF routes visible as `D EX` in Skynet domain.
- [ ] EIGRP routes visible as `O E1` in CyberDyne domain.
- [ ] Route tags applied and verified for both protocols.
- [ ] Full reachability between R4 and R5.
