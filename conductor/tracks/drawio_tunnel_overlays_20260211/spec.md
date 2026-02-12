# Specification: Draw.io Tunnel Overlay Line Styles

## Goal

Establish canonical visual styles for overlay/tunnel connections in topology diagrams. Tunnel lines must be visually distinct from physical links and should curve over intermediate devices to emphasize their logical (overlay) nature.

## Rules

### Line Style
- Smallest dotted lines (`strokeWidth=1; dashed=1; dashPattern=1 4`)
- Colors per tunnel type:
  - **GRE**: White (`#FFFFFF`)
  - **MPLS**: Orange (`#FF6600`)
  - **IPsec VPN**: Red (`#FF0000`)
  - **VXLAN**: Cyan (`#00AAFF`)
  - **L2TP**: Purple (`#AA00FF`)
  - Unknown/other: Yellow (`#FFFF00`)

### Routing
- Tunnel lines exit from the **top** of the source device and enter from the **top** of the target device.
- Two waypoints arc the line **above both devices** at `arc_y = min(src_y, dst_y) - 100`.
- This makes the tunnel visually "fly over" the physical layer.

### Legend
- The legend box must list each tunnel type with its color.

## Deliverables
1. Section 4.9 added to `.agent/skills/drawio/SKILL.md`.
2. `generate_topo.py` updated to support `tunnel_overlays` from baseline.yaml.
3. `labs/eigrp/baseline.yaml` updated with Lab 08 (and 09) GRE tunnel overlay.
4. EIGRP Lab 08 `topology.drawio` regenerated to verify.
