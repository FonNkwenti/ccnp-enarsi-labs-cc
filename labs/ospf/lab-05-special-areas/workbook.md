# CCNP ENCOR OSPF Lab 05: OSPF Special Area Types
**Student Workbook & Instructor Guide**

---

## 1. Concepts & Skills Covered

- Understand OSPF Stub and Totally Stubby area types.
- Configure Stub areas to filter Type 4 and Type 5 LSAs.
- Configure Totally Stubby areas to filter Type 3, 4, and 5 LSAs.
- Verify default route injection in special area types.
- Analyze the impact of area types on the OSPF Link-State Database (LSDB) and routing table.

---

## 2. Topology & Scenario

### ASCII Diagram
```
                    ┌─────────────────┐
                    │       R1        │
                    │    Hub / ABR    │
                    │  Lo0: 10.1.1.1  │
                    └───┬─────────┬───┘
                        │ Fa1/0   │ Fa1/1
                        │         │
           10.12.0.1/30 │ Area 0  │ 10.13.0.1/30
                        │         │
                        │         │ 10.13.0.2/30
                        │    ┌────┴────────┐
                        │    │     R3      │
                        │    │   Branch    │
                        │    │ 10.3.3.3/32 │
                        │    └────┬────────┘
                        │         │ Fa1/0
                        │         │ 10.37.0.1/30
                        │         │ Area 37
                        │         │ 10.37.0.2/30
                        │         │ Fa0/0
                 ┌──────┴─────────┘      │
                 │       R2              │       ┌──────────────┐
                 │ Backbone Router       │       │      R7      │
                 │  10.2.2.2/32          └───────┤     Stub     │
                 └─────────────────┘             │ 10.7.7.7/32  │
                                                 └──────────────┘
```

### Scenario Narrative
The **Skynet Global** network continues to expand. A new remote office has been established, represented by **R7**. This office is connected to the branch router **R3** via a relatively low-bandwidth link. To conserve resources on R7 and minimize OSPF overhead, the engineering team has decided to implement OSPF Special Area types for the link between R3 and R7 (Area 37).

Your goal is to first configure Area 37 as a standard OSPF **Stub Area** to block external routes, and then further optimize it by converting it into a **Totally Stubby Area** to block inter-area summary routes as well. You will verify how these changes affect the routing table and LSDB on R7, and how R7 maintains reachability to the rest of the network using an automatically injected default route.

### Device Role Table
| Device | Role | Platform | Loopback0 | New in Lab 05 |
|--------|------|----------|-----------|---------------|
| R1 | Hub / ABR | c7200 | 10.1.1.1/32 | No |
| R2 | Backbone Router | c3725 | 10.2.2.2/32 | No |
| R3 | Branch Router / ABR | c3725 | 10.3.3.3/32 | No |
| R7 | Stub Router | c3725 | 10.7.7.7/32 | Yes |

---

## 3. Hardware & Environment Specifications

### 3.1 Router Platform Table
| Device | Model | RAM | Image Name |
|--------|-------|-----|------------|
| R1 | c7200 | 512 MB | `c7200-adventerprisek9-mz.153-3.XB12.image` |
| R2 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R3 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |
| R7 | c3725 | 256 MB | `c3725-adventerprisek9-mz.124-15.T14.image` |

### 3.2 Cabling & Connectivity Table
| Local Device | Local Interface | Remote Device | Remote Interface | Subnet | Area |
|--------------|-----------------|---------------|------------------|--------|------|
| R1           | Fa1/0           | R2            | Fa0/0            | 10.12.0.0/30 | 0 |
| R2           | Fa0/1           | R3            | Fa0/0            | 10.23.0.0/30 | 1 |
| R1           | Fa1/1           | R3            | Fa0/1            | 10.13.0.0/30 | 0 |
| R3           | Fa1/0           | R7            | Fa0/0            | 10.37.0.0/30 | 37 |

### 3.3 Console Access Table
| Device | Port | Connection Command |
|--------|------|--------------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |
| R3 | 5003 | `telnet 127.0.0.1 5003` |
| R7 | 5007 | `telnet 127.0.0.1 5007` |

---

## 4. Base Configuration

> **This lab builds on Lab 04.** Ensure that OSPF Area 0 and Area 1 are correctly configured and all adjacencies are stable. R7 should be added with its basic OSPF configuration as per the initial-configs.

---

## 5. Lab Challenge: OSPF Special Area Types

### Objective 1: Implement OSPF Stub Area
Reduce the LSDB size on R7 by filtering external routes.
- Configure **Area 37** as a **Stub Area**. Remember that the stub flag must match on all routers in the area (**R3** and **R7**).
- Verify that the OSPF adjacency between R3 and R7 re-establishes.
- On **R7**, examine the routing table (`show ip route`). Note the absence of any external (E1/E2) routes (if any were present) and the presence of a new default route.
- On **R7**, examine the LSDB (`show ip ospf database`). Identify the LSA type used for the default route.

### Objective 2: Implement OSPF Totally Stubby Area
Further optimize Area 37 by filtering inter-area summary routes.
- On the ABR (**R3**), modify the Area 37 configuration to make it a **Totally Stubby Area**.
- Note: This change is only required on the ABR. The internal router (**R7**) remains configured as a standard stub.
- On **R7**, examine the routing table again. What happened to the Inter-Area (IA) routes?
- Verify that **R7** can still reach **R1's** loopback (10.1.1.1) and **R2's** loopback (10.2.2.2). How is this achieved?

### Objective 3: Analyze LSA Filtering
Examine the OSPF database to confirm filtering behavior.
- On **R7**, use `show ip ospf database` to compare the database content before and after the Totally Stubby configuration.
- Confirm that Type 3 LSAs (Summary Net) are now reduced to a single default route entry.

---

## 6. Verification & Analysis

| Command | Expected Outcome |
|---------|------------------|
| `show ip ospf database` | On R7, verify reduction in LSA types and counts. |
| `show ip route ospf` | On R7, confirm `O*IA 0.0.0.0/0` is present. |
| `show ip ospf interface` | Verify Area 37 is identified as a Stub area. |

---

## 7. Verification Cheatsheet

### 7.1 Verify Stub Area Status on R7
```bash
R7# show ip ospf | include Area 37
 Area 37 is a stub area
```

### 7.2 Verify Default Route on R7
Confirm that a default route is learned via OSPF.
```bash
R7# show ip route ospf
Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area 
       ...
Gateway of last resort is 10.37.0.1 to network 0.0.0.0

O*IA  0.0.0.0/0 [110/11] via 10.37.0.1, 00:05:21, FastEthernet0/0
```

### 7.3 Analyze LSDB on R7 (Totally Stubby)
```bash
R7# show ip ospf database

            OSPF Router with ID (10.7.7.7) (Process ID 1)

                Router Link States (Area 37)

Link ID         ADV Router      Age         Seq#       Checksum Link count
10.3.3.3        10.3.3.3        185         0x80000003 0x00E26D 1
10.7.7.7        10.7.7.7        180         0x80000003 0x0078DB 2

                Summary Net Link States (Area 37)

Link ID         ADV Router      Age         Seq#       Checksum
0.0.0.0         10.3.3.3        186         0x80000001 0x004A3D
```
*Note: Only Router LSAs for Area 37 and a single Summary LSA for the default route (0.0.0.0) are present.*

---

## 8. Troubleshooting Scenario

### The Fault
You configured `area 37 stub no-summary` on **R3**, but you forgot to configure `area 37 stub` on **R7**. The adjacency between R3 and R7 fails to form, even though the interfaces are Up/Up and can ping each other.

### The Mission
1. Use `show ip ospf neighbor` and `show ip ospf interface` to diagnose the issue.
2. Check the OSPF logs or use `debug ip ospf adj` to identify the Hello packet mismatch.
3. Correct the configuration to restore the adjacency.

---

## 9. Solutions (Spoiler Alert!)

### Objective 1: Implement OSPF Stub Area

<details>
<summary>Click to view R3 and R7 Configuration</summary>

```bash
! R3
configure terminal
router ospf 1
 area 37 stub
 end

! R7
configure terminal
router ospf 1
 area 37 stub
 end
```
</details>

### Objective 2: Implement OSPF Totally Stubby Area

<details>
<summary>Click to view R3 Configuration</summary>

```bash
! R3
configure terminal
router ospf 1
 area 37 stub no-summary
 end
```
</details>

---

## 11. Automated Fault Injection (Optional)

This lab includes automated scripts to inject troubleshooting scenarios.

**Quick Start**:
```bash
python3 scripts/fault-injection/inject_scenario_01.py  # Adjacency failure (Stub flag mismatch)
```

## 12. Lab Completion Checklist

- [ ] Area 37 configured as a Stub Area.
- [ ] Adjacency between R3 and R7 established with Stub flags.
- [ ] Default route verified in R7's routing table.
- [ ] Area 37 converted to a Totally Stubby Area on R3.
- [ ] IA routes filtered from R7's routing table.
- [ ] R7 reachability verified via default route.
- [ ] LSDB analysis completed on R7.
