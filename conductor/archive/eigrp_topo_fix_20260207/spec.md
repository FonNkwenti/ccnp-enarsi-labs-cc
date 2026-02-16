# Track Specification: Fix EIGRP Lab Topology Diagrams (04-09)

## Goal
Update the `topology.drawio` files for EIGRP Labs 04, 05, 06, 07, 08, and 09 to accurately reflect the devices, links, and addressing defined in `labs/eigrp/baseline.yaml`.

## Scope
- **Target Files:**
    - `labs/eigrp/lab-04-stub-wan-opt/topology.drawio`
    - `labs/eigrp/lab-05-authentication-advanced/topology.drawio`
    - `labs/eigrp/lab-06-filtering-control/topology.drawio`
    - `labs/eigrp/lab-07-redistribution/topology.drawio`
    - `labs/eigrp/lab-08-eigrp-over-vpn/topology.drawio`
    - `labs/eigrp/lab-09-dual-stack-migration/topology.drawio`
- **Content Standards:**
    - Must follow `drawio` skill standards.
    - Official Cisco icons.
    - Labels for hostnames, interfaces, IPs, subnets, and loopbacks.
    - Administrative info (AS numbers).

## Success Criteria
- Each lab directory contains an accurate `topology.drawio`.
- Exported `topology.png` files exist for each lab.
- Diagrams strictly match the configuration in `baseline.yaml` and the lab workbooks.
