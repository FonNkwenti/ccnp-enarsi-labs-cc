# Troubleshooting Challenges: EIGRP Lab 09

These challenges are designed to test your diagnostic skills. 

**Instructions:**
1. Inject a fault using the corresponding script (e.g., `python3 scripts/fault_inject_1.py`).
2. Identify and resolve the issue on the routers.
3. Once resolved, or to start over, run the refresh script: `python3 scripts/refresh_lab.py`.

## Challenge 1: The Invisible AF (Unicast Routing)
**Script:** `scripts/fault_inject_1.py`
**Symptom:** You've configured the EIGRP Named Mode `address-family ipv6` on R1 and R2, and assigned IPv6 addresses to the interfaces. However, `show ipv6 eigrp neighbors` is empty, and the router won't even let you enter certain IPv6 configuration modes.

**Goal:** Identify the global configuration command missing on R2 that prevents IPv6 routing from functioning.

---

## Challenge 2: Named Mode Identity Crisis
**Script:** `scripts/fault_inject_2.py`
**Symptom:** R1 and R2 have established an IPv4 adjacency, but the IPv6 adjacency won't form. `show eigrp address-family ipv6 neighbors` shows nothing. You've verified physical and IPv6 connectivity (pings work).

**Goal:** Investigate the `address-family` configuration under the Named Mode process on R2. Is the Autonomous System number correct for the IPv6 family?

---

## Challenge 3: Tunnel Vision (IPv6 over GRE)
**Script:** `scripts/fault_inject_3.py`
**Symptom:** The GRE tunnel between R1 and R6 is working for IPv4, but EIGRP IPv6 routes from R6 are not appearing on R1. `show ipv6 route eigrp` on R1 shows no routes via the tunnel.

**Goal:** Check the tunnel interface configuration on R6. Ensure IPv6 is properly enabled and that the tunnel is correctly participating in the IPv6 address family.
