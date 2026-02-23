# EIGRP Lab 10 — Capstone II: Comprehensive Troubleshooting

**Exam:** CCNP ENARSI 300-410
**Difficulty:** Advanced
**Estimated Time:** 120 minutes

---

## 1. Concepts & Skills Covered

### Blueprint Coverage

| Blueprint IDs | Topics |
|---|---|
| 1.9.b | Neighbor adjacency (troubleshoot misconfigurations) |
| 1.9.c | Loop-free path selection (verify FD/RD, detect loop conditions) |
| 1.9.d | EIGRP stub routing (identify misconfigurations) |
| 1.9.e | Load balancing (diagnose unequal-cost issues) |
| 1.9.f | Metrics (troubleshoot bandwidth/delay conflicts) |
| 1.1 | Administrative distance (verify correct route preference) |
| 1.2 | Route map (diagnose filtering issues) |
| 1.3 | Loop prevention (verify split horizon, route poisoning) |
| 1.5 | Summarization (detect and fix black holes) |

### Key Concepts

This final capstone integrates all EIGRP troubleshooting skills. You are presented with a **completely broken network** — one with 5+ concurrent faults. Using only show commands and your knowledge of EIGRP from Labs 01–09, you must:

1. Identify all faults using symptom analysis
2. Determine root causes systematically
3. Apply fixes without step-by-step guidance
4. Verify fixes restore full functionality

**Symptoms are provided, but root causes are not revealed in headings.**

---

## 2. Topology & Scenario

### Enterprise Scenario

Acme Corp deployed EIGRP using the exact configuration from Lab 09 (Capstone I). However, during a maintenance window, multiple configuration errors were introduced by different network engineers. The network is now partially broken:

- Some routers cannot reach certain destinations
- Some adjacencies are unstable
- Some routes use incorrect paths
- Some metrics are miscalculated
- Some filtering is overblocked or not applied
- Some AD values conflict

Your role: **Network Troubleshooter**

Using only show commands and your accumulated EIGRP knowledge, diagnose every fault and restore the network to full functionality. You have 120 minutes to troubleshoot all faults.

### Topology Reference

Same as Lab 09:
- **R1** (Hub): 10.0.0.1/32, connects to R2, R3, R4
- **R2** (Branch A): 10.0.0.2/32, 172.16.20/21.0/24, connects to R1 and R3
- **R3** (Branch B): 10.0.0.3/32, 172.16.30/31.0/24, connects to R1 and R2
- **R4** (Stub): 10.0.0.4/32, 192.168.4.0/24, connects to R1 only

---

## 3. Hardware & Environment Specifications

**Same as Lab 09** — refer to Capstone I for device details, cabling, IP addressing, and console access.

---

## 4. Base Configuration

**Initial State:**
- ✅ All IP addresses and loopback interfaces are correctly configured
- ✅ EIGRP classic mode is configured with faults
- ✅ Some network statements are correct; others are wrong
- ✅ Some adjacencies are missing due to AS mismatch or passive interfaces
- ✅ Filtering, summarization, and AD changes were attempted but have errors

**Known Faults (Symptoms, not Solutions):**
- R2 cannot reach R4's loopback (192.168.4.0/24)
- R1 and R3 have incomplete routing to R2's summarized subnets
- R2's manual summary route 172.16.20.0/23 is not advertised to neighbors (auto-summary fault)
- R4 is not configured as a stub, causing transit routing problems
- One adjacency is missing (AS mismatch or passive interface)
- Metric conflicts cause suboptimal path selection
- Split horizon may be blocking hub-spoke reachability
- Distribution or tagging errors suppress routes

---

## 5. Lab Challenge: Comprehensive Troubleshooting

### Your Task

**Fix the network using ONLY show commands and your accumulated knowledge. No guidance is provided.**

#### Step 1: Establish Your Baseline

Understand the current broken state:

```bash
# On each router, run:
show ip eigrp neighbors
show ip route eigrp
show ip eigrp topology
show run | section eigrp
```

Document:
- Which adjacencies are present/missing
- Which routes are present/missing
- Which routes use incorrect next-hops
- Any syntax errors or incomplete configurations

#### Step 2: Identify Faults Systematically

Use the following logical order:

1. **Adjacency Problems** (blocking all routes from/to a neighbor)
   - Check: AS number, K-values, passive interfaces, network statements

2. **Routing Table Gaps** (missing routes despite adjacencies)
   - Check: Network statements, auto-summary, filtering, passive interfaces

3. **Path Selection Issues** (routes exist but use wrong next-hop)
   - Check: Metrics, bandwidth/delay settings, AD values, variance

4. **Stub/Transit Problems** (stub is leaking routes or not receiving routes)
   - Check: Stub configuration, connected routes, adjacencies

5. **Summarization Issues** (summary not appearing or black hole)
   - Check: Network statements for loopbacks, summary-address commands, null0 routes

6. **Filtering Issues** (routes incorrectly blocked or not filtered)
   - Check: Prefix-lists, distribute-lists, direction (in/out)

7. **Loop Prevention Issues** (split horizon blocking needed routes)
   - Check: Split horizon status per interface, route propagation

#### Step 3: Fix Each Fault

For each identified fault:

1. **Diagnose** using show commands — understand the root cause
2. **Hypothesize** the fix based on your knowledge from Labs 01–08
3. **Apply** the configuration change
4. **Verify** the fix with follow-up show commands
5. **Document** the fix for your records

#### Step 4: Validate Full Restoration

After all fixes:

```bash
# Verify end-to-end reachability
R1# ping 10.0.0.2 source 10.0.0.1
R1# ping 10.0.0.3 source 10.0.0.1
R1# ping 10.0.0.4 source 10.0.0.1
R1# ping 172.16.20.1 source 10.0.0.1
R1# ping 172.16.21.1 source 10.0.0.1
R1# ping 172.16.30.1 source 10.0.0.1
R1# ping 172.16.31.1 source 10.0.0.1
R1# ping 192.168.4.1 source 10.0.0.1

R2# ping 10.0.0.3 source 10.0.0.2
R2# ping 10.0.0.4 source 10.0.0.2
R2# ping 192.168.4.1 source 10.0.0.2

R3# ping 10.0.0.4 source 10.0.0.3
# (Should fail — R3 blocks 192.168.4.0/24 via filtering)

R4# ping 10.0.0.2 source 10.0.0.4
R4# ping 10.0.0.3 source 10.0.0.4
```

All should succeed except R3→192.168.4.0/24 (intentional).

---

## 6. Verification & Analysis

### Verification Checklist (After All Fixes)

- [ ] R1 has 3 IPv4 EIGRP neighbors: R2 (10.12.0.2), R3 (10.13.0.2), R4 (10.14.0.2)
- [ ] R2 has 2 IPv4 EIGRP neighbors: R1 (10.12.0.1), R3 (10.23.0.2)
- [ ] R3 has 2 IPv4 EIGRP neighbors: R1 (10.13.0.1), R2 (10.23.0.1)
- [ ] R4 has 1 IPv4 EIGRP neighbor: R1 (10.14.0.1)
- [ ] All routers show "Passive" (P) state for all routes (no active reconvergence)
- [ ] R1 routing table includes:
  - 10.0.0.2, 10.0.0.3, 10.0.0.4 (loopbacks)
  - 172.16.20.0/23, 172.16.30.0/23 (summaries)
  - 192.168.4.0/24 (R4 loopback)
  - All link subnets
- [ ] R2 routing table includes:
  - 10.0.0.1, 10.0.0.3, 10.0.0.4 (loopbacks)
  - 172.16.30.0/23 (R3 summary, not /24s)
  - 192.168.4.0/24
  - All link subnets
- [ ] R3 routing table includes:
  - 10.0.0.1, 10.0.0.2, 10.0.0.4 (loopbacks)
  - 172.16.20.0/23 (R2 summary, not /24s)
  - Does NOT include 192.168.4.0/24 (filtered)
  - All link subnets
- [ ] R4 routing table includes:
  - 10.0.0.1, 10.0.0.2, 10.0.0.3 (loopbacks)
  - 172.16.20.0/23, 172.16.30.0/23 (summaries)
  - All link subnets
- [ ] R1 is recognized as having AD 80 on EIGRP internal routes
- [ ] R4 is recognized as a stub router by R1
- [ ] R2 has dual next-hops for R3 (via R1 and direct)
- [ ] No syntax errors in running config
- [ ] All pings succeed except R3→192.168.4.0/24 (intentional)

---

## 7. Verification Cheatsheet

| Command | Purpose | Expected Result |
|---|---|---|
| `show ip eigrp neighbors` | Verify IPv4 adjacencies | 3 neighbors (R1), 2 neighbors (R2/R3), 1 neighbor (R4) |
| `show ip route eigrp` | Verify routing table | All expected routes present |
| `show ip eigrp neighbors detail` | Verify neighbor details, K-values, stub status | K-values match, R4 shows "Stub" on R1 |
| `show ip eigrp topology` | Verify topology database | All routes P (Passive), correct FD/RD |
| `show ip route <prefix>` | Verify specific route | Correct next-hop and metric |
| `show ip split-horizon eigrp 100 Fa0/0` | Verify split horizon status on R1 Fa0/0 | Should show "disabled" |
| `show run \| section eigrp` | Verify EIGRP configuration | All network statements, stubs, AD, summaries present |
| `show ip prefix-list` | Verify filtering | BLOCK-R4-LO should exist with correct deny/permit |
| `ping <ip> source <source-ip>` | Test end-to-end connectivity | All succeed except R3→192.168.4.0/24 |

---

## 8. Solutions (Spoiler Alert!)

> This is an exam-style troubleshooting lab. You are expected to diagnose and fix all faults independently. Attempt the lab thoroughly before viewing solutions.

<details>
<summary>Click here ONLY after spending significant time troubleshooting.</summary>

### Common Faults and Fixes

**Fault 1: AS Number Mismatch on R4**
- **Symptom:** R4 has no EIGRP neighbors; R1 doesn't see R4 as a neighbor
- **Root Cause:** R4 EIGRP AS is 200 instead of 100
- **Fix:** `router eigrp 100` (remove the wrong AS 200 process and configure correct AS 100)

**Fault 2: R2 Auto-Summary Fault**
- **Symptom:** 172.16.20.0/23 summary route is missing from R1 and R3 routing tables. R2's routing table shows classful summary 172.16.0.0/8 in Null0 instead of 172.16.20.0/23.
- **Root Cause:** `auto-summary` is enabled on R2 (instead of `no auto-summary`), causing classful summarization that overrides the manual /23 summary
- **Fix:** Under `router eigrp 100` on R2: `no auto-summary`

**Fault 3: K-Value Mismatch on R3**
- **Symptom:** R3 adjacency with R1 is unstable or drops after forming
- **Root Cause:** K3 value is 0 on R3, but K3=1 on other routers (metric formula mismatch)
- **Fix:** Correct K-values on R3 to match R1 (K1=1, K2=0, K3=1, K4=0, K5=0)

**Fault 4: Passive Interface on R1 Fa0/0**
- **Symptom:** R2 cannot reach R3 via R1; R2 only knows about R3 directly
- **Root Cause:** R1 Fa0/0 is set as passive, preventing adjacency with R2 (or not advertising routes)
- **Fix:** Remove `passive-interface FastEthernet0/0` from R1 EIGRP config

**Fault 5: Loopback Networks Missing from EIGRP on R2**
- **Symptom:** R1 and R3 do not see 172.16.20.0/23 summary; instead see individual /24s or nothing
- **Root Cause:** Network statements for 172.16.20.0 and 172.16.21.0 are missing or incorrect on R2
- **Fix:** Add `network 172.16.20.0 0.0.0.255` and `network 172.16.21.0 0.0.0.255` on R2

**Fault 6: Summarization Command on Wrong Interface**
- **Symptom:** R2's loopbacks are not summarized; R1 sees individual /24s instead of /23
- **Root Cause:** Summary command configured on Fa0/1 (link to R3) instead of Fa0/0 (link to R1)
- **Fix:** Move or add `ip summary-address eigrp 100 172.16.20.0 255.255.254.0` to Fa0/0 on R2

**Fault 7: R4 Not Configured as Stub**
- **Symptom:** R4 advertises learned routes (transit path); other routers use R4 as a backup path
- **Root Cause:** `eigrp stub connected summary` is missing on R4
- **Fix:** Add `eigrp stub connected summary` to R4 EIGRP config

**Fault 8: Prefix-List Missing Permit Statement**
- **Symptom:** R3 cannot reach ANY external routes (not just 192.168.4.0/24); routing table is empty
- **Root Cause:** Prefix-list has deny 192.168.4.0/24 but missing the implicit permit all
- **Fix:** Add `ip prefix-list BLOCK-R4-LO seq 10 permit 0.0.0.0/0 le 32`

**Fault 9: Split Horizon Not Disabled on R1 Fa0/0**
- **Symptom:** R2 cannot reach R3 via R1; only direct link is used (split horizon suppresses R3's routes)
- **Root Cause:** Split horizon is still enabled on R1 Fa0/0
- **Fix:** Add `no ip split-horizon eigrp 100` to R1 Fa0/0 interface

**Fault 10: AD Not Modified on R1**
- **Symptom:** EIGRP routes show [90/XXX] instead of expected [80/XXX]
- **Root Cause:** `distance eigrp 80 170` command is missing from R1
- **Fix:** Add `distance eigrp 80 170` under `router eigrp 100` on R1

</details>

---

## 9. Troubleshooting Workflow

Use this systematic approach to diagnose and fix faults:

### Phase 1: Adjacency & Connectivity

1. Check if all expected neighbors are present:
   ```
   show ip eigrp neighbors
   ```

2. If a neighbor is missing:
   - Check the remote router's EIGRP config (AS, network statements, passive)
   - Check the link (up/up?), IP address, subnet match
   - Check running config for that router

3. If adjacency exists but is flapping:
   - Check K-values for mismatch
   - Check authentication settings

### Phase 2: Routing Table Completeness

1. Verify expected routes are in the table:
   ```
   show ip route eigrp
   ```

2. If routes are missing:
   - Verify they exist in the originating router's running config
   - Check for passive interfaces blocking advertisement
   - Check for filtering (prefix-list, distribute-list)
   - Check for auto-summary overriding manual summaries
   - Check for summarization (expected /23 not showing individual /24s?)

3. If route is in topology but not in routing table:
   - Verify it's not marked as Active (A) — if so, DUAL is reconverging
   - Check for splits: `show ip eigrp topology all-links`

### Phase 3: Path Selection & Metrics

1. Verify route next-hop is correct:
   ```
   show ip route <prefix>
   show ip eigrp topology <prefix>
   ```

2. If path is incorrect:
   - Check if better path exists in topology: `show ip eigrp topology <prefix> all-links`
   - Verify metrics (bandwidth, delay) on interfaces
   - Check AD modifications
   - Check variance settings

### Phase 4: Filtering & Control Plane

1. Verify filtering is working as expected:
   ```
   show ip prefix-list
   show run | section distribute-list
   ```

2. If filtering is incorrect:
   - Check direction: `in` or `out`?
   - Check interface: correct link?
   - Verify prefix-list sequences and implicit deny

### Phase 5: Special Features

1. Verify stub routers are recognized:
   ```
   show ip eigrp neighbors detail
   ```
   Look for "Stub router" in output.

2. Verify split horizon status:
   ```
   show ip split-horizon eigrp 100 <interface>
   ```

3. Verify summarization:
   ```
   show ip route <summary>
   show ip summary-address eigrp
   ```

---

## 10. Lab Completion Checklist

**Troubleshooting & Diagnosis**
- [ ] All 5+ faults identified and documented
- [ ] Root cause for each fault explained
- [ ] Systematic approach used (adjacencies first, then routing table, etc.)

**Configuration Fixes**
- [ ] All EIGRP AS numbers corrected (all AS 100)
- [ ] All network statements present and correct
- [ ] No passive interfaces blocking necessary links
- [ ] All K-values matching across all neighbors
- [ ] R4 configured as stub
- [ ] Loopbacks on R2/R3 in EIGRP network statements
- [ ] Summarization on correct interfaces (R2 Fa0/0, R3 Fa0/0)
- [ ] `no auto-summary` on R2 (Fault 2 — auto-summary overrides manual /23 summary)
- [ ] Prefix-list has explicit permit-all statement
- [ ] Filtering applied in correct direction (inbound on R3 Fa0/0)
- [ ] AD modified on R1 (`distance eigrp 80 170`)
- [ ] Split horizon disabled on R1 Fa0/0

**Verification**
- [ ] All adjacencies established and stable
- [ ] All routes present in routing tables (except filtered ones)
- [ ] All routes use correct next-hops
- [ ] No "Active" routes (all Passive)
- [ ] Summarization working (R2 and R3 show /23s, not /24s, on other routers)
- [ ] Filtering working (R3 blocks 192.168.4.0/24)
- [ ] Split horizon disabled (R2 has dual paths to R3)
- [ ] AD modification visible ([80/XXX] on EIGRP routes)
- [ ] Stub recognized (R1 shows R4 as stub)
- [ ] All pings succeed except R3→192.168.4.0/24

**End-to-End Success**
- [ ] Full IPv4 mesh connectivity
- [ ] Troubleshooting skills demonstrated
- [ ] All EIGRP concepts from Labs 01–09 integrated and validated
- [ ] Network is production-ready
