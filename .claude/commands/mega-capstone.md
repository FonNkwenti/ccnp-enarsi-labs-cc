Generate the CCNP ENARSI Mega Capstone — a single integrated topology spanning all 7 chapters.

## Pre-flight checks (REQUIRED — stop if any fail)

1. Read `memory/progress.md`
2. Verify ALL of the following chapters have Capstone I AND Capstone II with status **Approved**:
   - eigrp
   - ospf
   - bgp
   - redistribution
   - vpn
   - infrastructure-security
   - infrastructure-services
3. If any chapter is missing approved capstones: list which chapters/capstones are not yet approved and stop. Do not generate.

## If all checks pass

Use the `mega-capstone-creator` skill.

## After generation

Update `memory/progress.md`:
- Add a "Mega Capstone" section at the bottom with status **Review Needed**
- Set "Active Work → Last completed lab" to "mega-capstone"
- Set "Next action" to: "Review mega-capstone — approve before considering the series complete"
