# Troubleshooting Challenges: EIGRP Lab 06

These challenges are designed to test your diagnostic skills. 

**Instructions:**
1. Inject a fault using the corresponding script (e.g., `python3 scripts/fault_inject_1.py`).
2. Identify and resolve the issue on the routers.
3. Once resolved, or to start over, run the refresh script: `python3 scripts/refresh_lab.py`.

## Challenge 1: The Recursive Lookup Gap
**Script:** `scripts/fault_inject_1.py`
**Symptom:** R1 neighbor adjacency with R2 is UP, but R1 has NO EIGRP routes in its routing table. You've verified the `AUTHORIZED_NETS` prefix-list is applied.

**Goal:** Identify what is missing from the prefix-list that prevents R1 from installing ANY EIGRP routes. Hint: Think about how EIGRP calculates the next-hop.

---

## Challenge 2: The Implicit Deny Disaster
**Script:** `scripts/fault_inject_2.py`
**Symptom:** R3 has lost all routes from the rest of the network after a "minor" update to the `RM_FILTER_R3` route-map on R2. R3 only sees its locally connected networks.

**Goal:** Fix the route-map on R2 so that it only filters the intended prefix (R1's loopback) and allows everything else.

---

## Challenge 3: Broad Brush Filtering
**Script:** `scripts/fault_inject_3.py`
**Symptom:** R5 can no longer reach R2 or R1's loopbacks, even though the filter was only supposed to block the `10.0.x.x` infrastructure subnets.

**Goal:** Refine the access-list on R3 to ensure it only blocks the intended infrastructure ranges without accidentally catching the management loopbacks.
