# Troubleshooting Challenges: EIGRP Lab 08

These challenges are designed to test your diagnostic skills. 

**Instructions:**
1. Inject a fault using the corresponding script (e.g., `python3 scripts/fault_inject_1.py`).
2. Identify and resolve the issue on the routers.
3. Once resolved, or to start over, run the refresh script: `python3 scripts/refresh_lab.py`.

## Challenge 1: The Infinite Loop (Recursive Routing)
**Script:** `scripts/fault_inject_1.py`
**Symptom:** You see a console message on R1 or R6 stating "%TUN-5-RECURDOWN: Tunnel8 temporarily disabled due to recursive routing". The EIGRP adjacency never stays UP.

**Goal:** Identify why the router is trying to reach the tunnel destination THROUGH the tunnel itself and fix the EIGRP network advertisements.

---

## Challenge 2: The Giant's Burden (MTU Mismatch)
**Script:** `scripts/fault_inject_2.py`
**Symptom:** Small pings across the tunnel work, but large pings (e.g., `ping 172.16.16.2 size 1500`) fail. EIGRP neighbor status flaps when large routing updates are exchanged.

**Goal:** Correct the IP MTU settings on the tunnel interfaces to account for GRE overhead and ensure large updates can pass.

---

## Challenge 3: Destination Unreachable
**Script:** `scripts/fault_inject_3.py`
**Symptom:** Tunnel8 is "up/down" on R1. `show interface tunnel 8` shows the tunnel is up, but line protocol is down. Pings to the tunnel source/destination physical IPs (10.0.16.x) are failing.

**Goal:** Investigate the physical connectivity or static routing between R1 and R6 that is preventing the tunnel from establishing.
