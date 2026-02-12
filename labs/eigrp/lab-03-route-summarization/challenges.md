# Troubleshooting Challenges: EIGRP Lab 03

These challenges are designed to test your diagnostic skills. 

**Instructions:**
1. Inject a fault using the corresponding script (e.g., `python3 scripts/fault_inject_1.py`).
2. Identify and resolve the issue on the routers.
3. Once resolved, or to start over, run the refresh script: `python3 scripts/refresh_lab.py`.

## Challenge 1: The Null0 Blackhole
**Script:** `scripts/fault_inject_1.py`
**Symptom:** R1 has a route for the summarized 172.16.0.0/16 regional network, but it's pointing to `Null0` instead of R7. Consequently, no one can reach the subnets behind R7.

**Goal:** Identify why R1 has locally generated a summary route for a prefix it should be learning from R7, and restore the correct path.

---

## Challenge 2: Summary AD Sabotage
**Script:** `scripts/fault_inject_2.py`
**Symptom:** You've configured summarization on R3, but the summary route is not appearing in the routing tables of R2 or R1. R3's console shows that the neighbor relationship with R2 is stable.

**Goal:** Investigate the administrative distance settings for the summary on R3. Is the summary "too expensive" to be used?

---

## Challenge 3: Overly Aggressive Boundary
**Script:** `scripts/fault_inject_3.py`
**Symptom:** R7 is configured to summarize 172.16.0.0/16, but it is also accidentally summarizing the 10.0.17.0/30 transit link. R1 and R7 have lost their EIGRP adjacency.

**Goal:** Correct the summarization mask or command on R7 to ensure that management and transit networks are not accidentally suppressed by the regional summary.
