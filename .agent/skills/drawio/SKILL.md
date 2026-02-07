---
name: drawio
description: Standards and workflows for creating and managing network diagrams using Draw.io.
---

# Draw.io Diagram Skill

## 1. Locations

Store diagrams in the following directories based on their type:

- **Topology Diagrams**: `labs/[chapter]/[lab-folder]/topology.drawio`
  - Use for network topologies, physical cabling, and logical connectivity.
- **Flow Diagrams**: `labs/[chapter]/[lab-folder]/flow-[description].drawio`
  - Use for packet flows, process charts, and logic flows.

## 2. File Formats

For every diagram, you must maintain two files with the **exact same basename**:

1.  **Source File (`.drawio`)**: The editable XML format.
2.  **Exported Image (`.png`)**: The visual representation for documentation.
    - *Note:* When exporting to PNG, ensure "Include path" or "copy of my drive" options are unselected if using the web version, but for local usage, a standard transparent background PNG is preferred.

## 3. Naming Conventions

- Use **kebab-case** for all filenames.
- **Pattern**: `[lab-name]-[diagram-type].extension`
- **Examples**:
  - `eigrp-basic-adjacency-topology.drawio`
  - `eigrp-basic-adjacency-topology.png`
  - `packet-flow-vlan-routing.drawio`

## 4. Design Standards

- **Icons**: Use official Cisco Network Topology Icons.
  - **Technical Implementation**: When generating XML, use the following `style` strings:
    - **Router**: `shape=mxgraph.cisco.routers.router;fillColor=#036897;strokeColor=#ffffff;`
    - **L3 Switch**: `shape=mxgraph.cisco.switches.layer_3_switch;fillColor=#036897;strokeColor=#ffffff;`
    - **L2 Switch**: `shape=mxgraph.cisco.switches.workgroup_switch;fillColor=#036897;strokeColor=#ffffff;`
    - **Cloud/Internet**: `shape=mxgraph.cisco.misc.cloud;fillColor=#036897;strokeColor=#ffffff;`
- **Colors**:
  - **Routers**: Blue (`#036897`).
  - **Annotation Boxes**: Light Yellow (`#fff2cc`) with Gold border (`#d6b656`).
- **Mandatory Labeling**:
  - **Hostnames**: Bold, 11pt, positioned directly above or below the icon.
  - **Interfaces**: 10pt, positioned at **each end** of every link (e.g., `Fa0/0`, `Gi1/1`).
  - **IP Addresses**: 10pt, positioned next to the interface. For point-to-point links, use the host part (e.g., `.1`, `.2` or `::1`, `::2`).
  - **Subnets**: 9pt, positioned near the center of the link or in a callout box. Include both IPv4 and IPv6 for dual-stack labs.
  - **Loopbacks**: 10pt, listed clearly below the hostname or in a dedicated info box.
  - **Administrative Info**: EIGRP AS numbers, OSPF Areas, and BGP ASNs must be clearly labeled using annotation boxes or boundary markers.

## 5. Workflow

### Creating a New Diagram
1.  Open Draw.io (Desktop or Web).
2.  Create the diagram following design standards.
3.  **Validation Checklist**:
    - [ ] Does every device have a hostname and Loopback IP?
    - [ ] Does every link have interface names on BOTH ends?
    - [ ] Does every link have host IP bits on BOTH ends?
    - [ ] Is the subnet ID clearly visible for every segment?
    - [ ] Are protocol boundaries (Areas, AS) clearly marked?
4.  Save the editable file as `.drawio` in the appropriate subdirectory.
5.  Export the diagram as a `.png` (Transparent Background, 200% Zoom/Scale 2.0 for high DPI) to the same directory.
6.  Link the PNG in your README.md files.

### Updating a Diagram
1.  Open the existing `.drawio` file.
2.  Make necessary modifications.
3.  Save the `.drawio` file.
4.  Re-export to `.png`, overwriting the existing image.
