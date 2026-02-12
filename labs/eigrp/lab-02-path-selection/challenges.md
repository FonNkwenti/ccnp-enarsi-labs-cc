# Troubleshooting Challenges: EIGRP Lab 02

These challenges are designed to test your diagnostic skills. 

**Instructions:**
1. Inject a fault using the corresponding script (e.g., `python3 scripts/fault_inject_1.py`).
2. Identify and resolve the issue on the routers.
3. Once resolved, or to start over, run the refresh script: `python3 scripts/refresh_lab.py`.

## Challenge 1: The Invisible Backup
**Script:** `scripts/fault_inject_1.py`
**Symptom:** You have configured `variance 10` on R1 to enable load balancing to R3 (3.3.3.3/32), but the routing table still only shows one path via R2. You've verified that the redundant link (Fa1/1) is up and EIGRP adjacent.

**Goal:** Identify why the redundant path is not being used for load balancing, even with a high variance. Hint: Check the Feasibility Condition in the topology table.

---

## Challenge 2: Accidental Detour
**Script:** `scripts/fault_inject_2.py`
**Symptom:** Traffic from R1 to R3's loopback (3.3.3.3) is taking a very strange path through another remote site (simulated by high delay on standard links). The primary link is up, but the metric is unexpectedly high.

**Goal:** Find the interface configuration on R1 that has artificially inflated the metric for the primary path.

---

## Challenge 3: Metric Madness
**Script:** `scripts/fault_inject_3.py`
**Symptom:** R1 is no longer learning routes from R3 over the direct link (Fa1/1), although the neighbor relationship is "UP". Pings to R3's interface 10.0.13.2 work, but the 3.3.3.3/32 prefix is only learned via R2.

**Goal:** Investigate why R1 is ignoring the prefix over the direct link. Check for prefix-filtering or offset-lists that might have been applied.
