# Cisco Network Troubleshooting Skill

A systematic approach to diagnosing and resolving Cisco network faults using structured methodologies from Cisco curriculum.

## Overview

This skill implements a rigorous four-phase troubleshooting process that ensures:
- **Systematic diagnosis** - No random "guess and check" 
- **Evidence-based decisions** - Every hypothesis is tested
- **Complete documentation** - Full audit trail for knowledge management
- **Professional resolution** - Meets enterprise change management standards

## The Four Phases

### Phase I: Problem Definition & Assessment
Transform vague symptoms ("network is down") into precise technical problem statements with specific symptoms, scope, and timeline.

### Phase II: Methodology Selection
Choose the optimal approach from five proven methodologies:
- **Top-Down**: Application layer issues (DNS, HTTP, email)
- **Bottom-Up**: Physical layer problems (cables, new installations)
- **Divide & Conquer**: Unknown layer, start at Layer 3 with ping
- **Follow Traffic Path**: Multi-hop routing, WAN issues, ACL blocking
- **Compare Configurations**: Similar devices, one works, one doesn't

### Phase III: Diagnostic Execution
Systematically gather information, establish baselines, eliminate valid causes, hypothesize and test, and verify the resolution.

### Phase IV: Resolution & Reporting
Generate comprehensive resolution reports including:
- Incident summary with clear problem statement
- Methodology applied and rationale
- Chronological diagnostic log
- Root cause analysis with technical details
- Resolution actions with actual commands used
- Testing and verification results
- Lessons learned and preventive recommendations

## When to Use This Skill

**Use for**:
- Network connectivity failures
- Routing protocol issues
- Configuration problems
- Performance degradation
- Service outages
- Post-maintenance validation failures
- Any reactive network troubleshooting

**Don't use for**:
- Network design (different skill needed)
- Security hardening (different skill needed)
- Capacity planning (different skill needed)
- Routine monitoring (different skill needed)

## Example Usage

Simply present a network problem to Claude with this skill enabled:

```
"Users in Building A cannot access the file server at 10.10.10.5. 
The issue started after this morning's maintenance window."
```

Claude will:
1. Clarify the problem with specific questions
2. Select the appropriate troubleshooting methodology
3. Systematically diagnose the issue
4. Provide a complete resolution report

## Evaluation Test Cases

The skill includes 6 comprehensive test scenarios:
1. **VLAN routing issue** - Testing traffic path methodology
2. **New router installation** - Testing bottom-up approach
3. **Application layer failure** - Testing top-down approach
4. **OSPF flapping** - Testing protocol-specific diagnosis
5. **Partial reachability** - Testing route filtering issues
6. **Configuration drift** - Testing compare configurations

Run evaluations using:
```bash
claude eval cisco-troubleshooting
```

## Key Features

✅ **Structured approach** - Follows Cisco curriculum best practices  
✅ **Methodology selection** - Chooses the right diagnostic strategy  
✅ **Complete documentation** - Enterprise-grade resolution reports  
✅ **Verification focus** - Always confirms resolution before closing  
✅ **Lessons learned** - Feeds back into organizational knowledge  
✅ **Prevents new problems** - Disciplined approach reduces mistakes  

## Professional Benefits

- Reduces Mean Time To Repair (MTTR)
- Provides compliance audit trails
- Builds team knowledge base
- Trains junior engineers
- Prevents repeat incidents
- Supports change management processes

## Integration with Change Management

Every resolution report includes:
- Root cause tracing to recent changes
- Configuration backup recommendations
- Preventive measure suggestions
- Documentation update requirements
- Monitoring enhancement proposals

## File Structure

```
cisco-troubleshooting-skill/
├── SKILL.md              # Main skill definition
├── README.md             # This file
└── evals/
    ├── evals.json        # Test scenarios
    └── files/            # Supporting files for evals
```

## Contributing

To improve this skill:
1. Run evaluations on real-world scenarios
2. Note any gaps in methodology coverage
3. Suggest additional diagnostic commands or tools
4. Propose new evaluation scenarios
5. Share lessons learned from production use

## License

This skill is designed for professional network engineers and IT support teams working with Cisco networking equipment.

---

**Remember**: In networking, discipline and documentation separate professionals from hobbyists. This skill enforces that discipline at every step.