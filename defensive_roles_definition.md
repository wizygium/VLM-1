# Handball Defensive Roles Definition

## Overview
Defensive formations in handball consist of **6 defensive roles (D1-D6)** that work together to prevent the attacking team from scoring. Each role has a typical zone and may move to adjacent zones as needed to cover gaps or disrupt play.

**Important Notes:**
- Defensive roles are **positional**, not tied to specific players
- Players may **switch roles** during play as needed
- Roles may be **unfilled** if the defending team has suspended players
- Zones overlap because defenders must cover multiple areas

## Defensive Role Definitions

### **D1 - Left Wing Defender**
- **Primary Zone**: Zone 1 (far left, between 6m-9m)
- **Allowed Movement Zones**: 1, 2, 6, 7
- **Responsibility**: Cover left wing attacker, prevent wing penetration
- **Positioning**: Typically slides between 6m line (zone 1 interior) and 9m area (zone 6)

### **D2 - Left-Center Defender**
- **Primary Zone**: Zone 2 (left-center, between 6m-9m)
- **Allowed Movement Zones**: 1, 2, 3, 6, 7, 8
- **Responsibility**: Cover left-center gaps, support D1 and D3
- **Positioning**: Flexible role that can slide to wings or center as needed

### **D3 - Center Defender**
- **Primary Zone**: Zone 3 (center, between 6m-9m)
- **Allowed Movement Zones**: 2, 3, 4, 7, 8, 9
- **Responsibility**: Protect center of goal, pivot marking, coordinate defense
- **Positioning**: Central position, may need to cover wide gaps when wings penetrate

### **D4 - Right-Center Defender**
- **Primary Zone**: Zone 4 (right-center, between 6m-9m)
- **Allowed Movement Zones**: 3, 4, 5, 8, 9, 10
- **Responsibility**: Cover right-center gaps, support D3 and D5
- **Positioning**: Flexible role mirroring D2 on opposite side

### **D5 - Right Wing Defender**
- **Primary Zone**: Zone 5 (far right, between 6m-9m)
- **Allowed Movement Zones**: 4, 5, 9, 10
- **Responsibility**: Cover right wing attacker, prevent wing penetration
- **Positioning**: Mirrors D1 on opposite side

### **D6 - Advanced Defender (Pivot/Playmaker Defender)**
- **Primary Zone**: Zone 8 (center back, between 9m-10m)
- **Allowed Movement Zones**: 2, 3, 4, 7, 8, 9
- **Responsibility**: Step out to disrupt back court play, close central gaps on 6m line
- **Positioning**: Most dynamic role - steps out to 9m (zone 8) or drops to 6m line (zones 2, 3, 4)

## Defensive Formation Types

### **6-0 Sliding Defense** (Most Common)
All 6 defenders play along the 6m line:
- **D1**: Zone 1 (may extend to zone 2)
- **D2**: Zone 2
- **D3**: Zone 3
- **D4**: Zone 4
- **D5**: Zone 5 (may extend to zone 4)
- **D6**: Typically zone 3, may also be in zones 2 or 4

**Characteristics:**
- All defenders on or near 6m line
- Defenders slide laterally to cover ball movement
- May leave far wing open (opposite side from ball)
- Strong against pivot play and close shots
- Vulnerable to long-range shots from 9m

### **5-1 Defense**
5 defenders on 6m line, 1 advanced defender:
- **D1-D5**: Zones 1-5 (on 6m line)
- **D6**: Zone 8 (stepped out to 9m area)

**Characteristics:**
- D6 steps out to pressure playmaker/center back
- Creates gaps on 6m line that D2-D4 must cover
- Disrupts back court passing
- Vulnerable if D6 beaten

### **3-2-1 or Other Variations**
Less common formations with multiple advanced defenders or specialized setups.

## Zone Overlap and Coverage

```
        GOAL (Zone 0)
    ═══════════════════════════
         6m LINE DEFENSE
    [D1]  [D2]  [D3]  [D4]  [D5]
     1-2   2-3    3    3-4   4-5
         ↑
        [D6] - May drop to 2,3,4
         or step to 7,8,9
    
         9m LINE AREA
    D1   D2    D6    D4    D5
    6-7  7-8    8    8-9   9-10
```

## Suspended Players

When defending team has suspended player(s):
- **5v6 (1 suspension)**: One defensive role unfilled
  - Typically remove D1 or D5 (wing defender)
  - Remaining defenders spread to cover larger zones
- **4v6 (2 suspensions)**: Two defensive roles unfilled
  - Often both wings (D1, D5) or wings + one center
  - Defense becomes highly vulnerable

**Tracking**: In JSON, unfilled roles should be marked as `null` or omitted from defensive_formation object.

## Visual Recognition Tips

When analyzing video:
1. **Count defenders**: Identify how many defenders are actively positioned
2. **Identify 6m line**: Look for the semi-circular 6m arc
3. **Check for stepped-out defenders**: Any defender beyond the 6m line is likely D6
4. **Track lateral movement**: Defenders slide left/right following the ball
5. **Look for gaps**: Unfilled zones indicate suspended players or intentional spacing

## Formation Naming Convention

In JSON, defensive formations can be described as:
- `"6-0 sliding"`: All defenders on 6m line
- `"5-1"`: 5 on 6m, 1 advanced
- `"5v6 (right wing gap)"`: 5 defenders due to suspension, gap on right
- `"4v6 (both wings)"`: 4 defenders due to suspensions
