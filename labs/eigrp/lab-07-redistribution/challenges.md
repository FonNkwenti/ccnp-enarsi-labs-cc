# Troubleshooting Challenges: EIGRP Lab 07

These challenges are designed to test your diagnostic skills. 

**Instructions:**
1. Inject a fault using the corresponding script (e.g., `python3 scripts/fault_inject_1.py`).
2. Identify and resolve the issue on the routers.
3. Once resolved, or to start over, run the refresh script: `python3 scripts/refresh_lab.py`.

## Challenge 1: The Infinite Distance (Seed Metrics)
**Script:** `scripts/fault_inject_1.py`
**Symptom:** R1 is successfully learning CyberDyne (OSPF) routes, but R2 and R3 have no external (D EX) routes in their routing tables. R1's `router eigrp 100` configuration shows redistribution is active.

**Goal:** Identify why the OSPF routes are not being propagated into the EIGRP domain and fix the metric issue.

---

## Challenge 2: Tagged Out (Redistribution Loop Prevention)
**Script:** `scripts/fault_inject_2.py`
**Symptom:** You've implemented a complex route-map to prevent loops, but now R4 (OSPF) is not receiving any Skynet routes. You see tag `222` in the configuration, but no external LSAs on R4.

**Goal:** Determine if the loop-prevention route-map is being too restrictive and blocking legitimate redistribution.

---

## Challenge 3: Subnet Scarcity
**Script:** `scripts/fault_inject_3.py`
**Symptom:** R4 can reach R1's directly connected interfaces, but it cannot see the EIGRP loopbacks (2.2.2.2, 3.3.3.3) or the stub networks. 

**Goal:** Find the missing keyword in the OSPF redistribution command on R1 that is preventing classless subnets from being advertised.
