# Troubleshooting Challenges: EIGRP Lab 01

These challenges are designed to test your diagnostic skills. 

**Instructions:**
1. Inject a fault using the corresponding script (e.g., `python3 scripts/fault_inject_1.py`).
2. Identify and resolve the issue on the routers.
3. Once resolved, or to start over, run the refresh script: `python3 scripts/refresh_lab.py`.

## Challenge 1: The "Ghost" Neighbor
**Script:** `scripts/fault_inject_1.py`
**Symptom:** R1 and R2 are connected, but `show ip eigrp neighbors` on R1 shows no neighbors. Pings between the physical interfaces (10.0.12.1 and 10.0.12.2) are successful.

**Goal:** Identify the protocol-level mismatch preventing the adjacency and restore connectivity.

---

## Challenge 2: The Weight of the World (K-Values)
**Script:** `scripts/fault_inject_2.py`
**Symptom:** You see console messages on R2 indicating "K-value mismatch". The adjacency with R3 flap continuously or never establishes.

**Goal:** Determine which K-values are mismatched and reset them to the default enterprise standard.

---

## Challenge 3: Silent Treatment
**Script:** `scripts/fault_inject_3.py`
**Symptom:** R2 shows an adjacency with R3, but R3 shows no neighbors on the link to R2. No EIGRP routes from R2 are appearing in R3's routing table.

**Goal:** Find the interface configuration error on R2 that is suppressing EIGRP Hello packets on a transit link.
