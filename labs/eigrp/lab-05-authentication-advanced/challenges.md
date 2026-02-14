# Troubleshooting Challenges: EIGRP Lab 05

These challenges are designed to test your diagnostic skills.

**Instructions:**
1. Inject a fault using the corresponding script (e.g., `python3 scripts/fault_inject_1.py`).
2. Identify and resolve the issue on the routers.
3. Once resolved, or to start over, run the refresh script: `python3 scripts/refresh_lab.py`.

## Challenge 1: The "Secret" Mismatch (MD5)
**Script:** `scripts/fault_inject_1.py`
**Symptom:** R1 and R2 are physically connected, but the EIGRP adjacency has dropped. `show ip eigrp neighbors` is empty on both sides. Console logs on R1 show "authentication bad key".

**Goal:** Identify why MD5 authentication is failing and restore the secure adjacency.

---

## Challenge 2: Tagging & Offsets Gone Wrong
**Script:** `scripts/fault_inject_2.py`
**Symptom:** R1 is successfully receiving routes from R5, but they are not being tagged with `555`, and consequently, the Offset List is not applying the expected metric penalty.

**Goal:** Find where the tagging process is failing (likely on R3) and ensure that R1 receives the routes with the correct tag.

---

## Challenge 3: The Phantom Penalty
**Script:** `scripts/fault_inject_3.py`
**Symptom:** R1's offset list appears to be active, but the metric penalty is being applied to the wrong routes. Routes from R5 that should be penalized are unaffected, while other routes are unexpectedly inflated.

**Goal:** Investigate the route-map `MATCH_TAG` on R1. Determine if the tag value being matched is correct (should be `555`), and fix the mismatch.

---

## Solutions (Spoiler Alert!)

### Challenge 1: The "Secret" Mismatch (MD5) — Solution

**Symptom:** R1 and R2 are physically connected, but the EIGRP adjacency has dropped. `show ip eigrp neighbors` is empty on both sides. Console logs on R1 show "authentication bad key".

**Root Cause:** The MD5 key-chain password was changed from `SkynetSecret` to `WRONG_PASSWORD` on R2, causing authentication failure.

**Solution:**

On **R2**, correct the key-chain password to match R1:

```bash
R2# configure terminal
R2(config)# key chain SKYNET_MD5
R2(config-keychain)# key 1
R2(config-keychain-key)# key-string SkynetSecret
R2(config-keychain-key)# exit
R2(config-keychain)# exit
R2(config)# end
R2# write memory
```

**Verification:**

```bash
R1# show ip eigrp neighbors detail
EIGRP-IPv4 Neighbors for AS 100
H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
                                                   (sec)         (ms)       Cnt Num
0   10.0.12.2               Fa1/0                    13 00:02:15   15   200  0  25
   Version 15.3/2.0, Retrans: 0, Retries: 0, Prefixes: 8
   Authentication MD5, key-chain "SKYNET_MD5"
```

The neighbor adjacency should re-establish and show MD5 authentication active.

---

### Challenge 2: Tagging & Offsets Gone Wrong — Solution

**Symptom:** R1 is successfully receiving routes from R5, but they are not being tagged with `555`, and consequently, the Offset List is not applying the expected metric penalty.

**Root Cause:** The `distribute-list route-map TAG_R5 out` was removed from the EIGRP router configuration on R3, preventing the route-map from being applied to routes sent to R1.

**Solution:**

On **R3**, re-apply the distribute-list route-map configuration:

```bash
R3# configure terminal
R3(config)# router eigrp 100
R3(config-router)# distribute-list route-map TAG_R5 out FastEthernet0/0
R3(config-router)# exit
R3(config)# end
R3# write memory
```

**Verification:**

Verify on **R1** that the routes from R5 are now tagged with `555`:

```bash
R1# show ip eigrp topology 5.5.5.5/32
EIGRP-IPv4 Topology Entry for AS 100 for 5.5.5.5/32
  State is Reply Pending, Query origin flag is 1, 1 Successor(s), FD is 1282560
  Descriptor Cards:
  10.0.12.2 (FastEthernet1/0), from 10.0.12.2, Send flag is 0x0
      Composite metric is (1282560/1024000), Route is Internal
      Vector metric:
        ...
        Route tag is 555
```

The tag `555` should now appear in the topology table. Verify the offset list is applying:

```bash
R1# show ip eigrp topology 5.5.5.5/32 | include "Composite metric"
Composite metric is (1782560/1024000), route is Internal
```

The composite metric should be increased by 500000 due to the offset list (1024000 + 500000 = 1524000 for the second value, reflecting the offset applied).

---

### Challenge 3: The Phantom Penalty — Solution

**Symptom:** R1's offset list appears to be active, but the metric penalty is being applied to the wrong routes. Routes from R5 that should be penalized are unaffected, while other routes are unexpectedly inflated.

**Root Cause:** The route-map `MATCH_TAG` on R1 was modified to match tag `999` instead of the correct tag value `555`. Since R5 routes are tagged with `555`, they don't match the route-map and the offset list isn't applied to them.

**Solution:**

On **R1**, correct the tag value in the MATCH_TAG route-map:

```bash
R1# configure terminal
R1(config)# route-map MATCH_TAG permit 10
R1(config-route-map)# no match tag 999
R1(config-route-map)# match tag 555
R1(config-route-map)# exit
R1(config)# end
R1# write memory
```

**Verification:**

Verify the corrected route-map configuration:

```bash
R1# show route-map MATCH_TAG
route-map MATCH_TAG, permit, sequence 10
  Match clauses:
    tag 555
  Set clauses:
  Policy routing matches: 0 packets, 0 bytes
```

Verify that the offset list is now correctly applied to routes tagged with `555`:

```bash
R1# show ip eigrp topology 5.5.5.5/32
EIGRP-IPv4 Topology Entry for AS 100 for 5.5.5.5/32
  State is Reply Pending, Query origin flag is 1, 1 Successor(s), FD is 1782560
  Descriptor Cards:
  10.0.12.2 (FastEthernet1/0), from 10.0.12.2, Send flag is 0x0
      Composite metric is (1782560/1024000), Route is Internal
      ...
      Route tag is 555
```

The composite metric should now include the offset penalty (1024000 + 500000 = 1524000 for the second value). Other routes not tagged with `555` should return to their original metrics without the penalty.
