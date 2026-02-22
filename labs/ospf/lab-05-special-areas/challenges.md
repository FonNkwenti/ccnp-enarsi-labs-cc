# Troubleshooting Challenges: OSPF Special Area Types

## Challenge 1: The Stubborn Adjacency

### The Fault
After attempting to convert Area 37 into a stub area, the adjacency between **R3** and **R7** has failed. R3 shows the neighbor in `EXSTART` or `DOWN` state, and eventually, it disappears from the neighbor list.

### Symptoms
- `show ip ospf neighbor` on R3 and R7 shows no adjacency for the 10.37.0.0/30 link.
- Interfaces are `Up/Up` and can ping each other.

### The Mission
1. Identify why the adjacency is failing.
2. Recall the specific OSPF Hello packet fields that must match for an adjacency to form.
3. Correct the configuration to restore the adjacency.

### Goal
Restore the OSPF adjacency between R3 and R7 as a **Stub Area**.

---

## Challenge 2: The Missing Inter-Area Routes

### The Fault
You have successfully established the adjacency as a stub area. Now, the requirement is to further reduce the routing table on **R7** by making Area 37 a **Totally Stubby Area**. You applied the configuration on the ABR (**R3**), but **R7** still shows all the IA routes in its routing table.

### Symptoms
- `show ip route ospf` on R7 still shows routes like `10.1.1.1/32` (R1) and `10.2.2.2/32` (R2) as `O IA`.

### The Mission
1. Explain why R7 is still receiving these routes despite R3 being configured with `area 37 stub no-summary`.
2. Verify if the `no-summary` keyword was correctly applied and if the OSPF process was cleared if necessary.
3. Ensure that R7 is receiving a default route instead of specific inter-area routes.

### Goal
Confirm that R7 has a single `O*IA 0.0.0.0/0` route and no other `O IA` routes.
