# Handball Court Zone Definitions

## Overview
The handball court is divided into **14 numbered zones (0-13)** for tracking player positions and ball movement during game analysis. Zones are defined relative to the attacking team's perspective, with the goal being defended at the near end.

## Zone Layout

```
                    GOAL (DEFENDING)
    ═══════════════════════════════════════════
                        [0]
         ┌──────────────║──────────────┐
         │                             │
         │           (6m D)            │
         └──────────────║──────────────┘
              6m LINE (D-LINE)
    
    [1]  [2]  [ 3 ]  [ 4 ]  [5]
         └────────────────────┘
         (Between 6m and 9m)
    
    [6]  [7]  [ 8 ]  [ 9 ]  [10]  
         └────────────────────┘
              9m LINE
    
         [11]    [12]    [13]
         └──────────────────┘
          ~10m+ DISTANCE
    
                    MIDCOURT
```

## Detailed Zone Descriptions

### **Goal Zone (0)**
- **Zone 0**: At the goal (goalkeeper position, goal mouth)

### **6m-8m Zones (1-5)** - Wing & Close Attack Area
Located **between the 6m D-line and approx 8m** (1m inside the 9m line).

- **Zone 1**: Far left position (left wing area)
- **Zone 2**: Left-center position
- **Zone 3**: Center position (Aligned with 3m flat section of 6m line)
- **Zone 4**: Right-center position
- **Zone 5**: Far right position (right wing area)

### **8m-10m Zones (6-10)** - Back Court Positions
Located from **8m to ~10m** depth.
**CRITICAL**: Players **standing ON the 9m line** are considered in these zones.

- **Zone 6**: Far left back position (Left Back area)
- **Zone 7**: Left central back position
- **Zone 8**: Center back position (Playmaker/CB) (Aligned with 3m flat section of 9m line)
- **Zone 9**: Right central back position
- **Zone 10**: Far right back position (Right Back area)

### **10m+ Zones (11-13)** - Deep Court
Located beyond the 9m line (10m+ from goal).

- **Zone 11**: Left deep position
- **Zone 12**: Center deep position (Aligned with goal width)
- **Zone 13**: Right deep position

### **Central Zone Identification (3, 8, 12)**
- **Visual Key**: Look for the **flat 3-meter segments** in the middle of the 6m and 9m lines.
- These segments run parallel to the goal line and align with the goal posts.
- Players within this central channel belong to Zones 3, 8, or 12.

## Usage Guidelines

### For Vision Models (Gemini Context)
When analyzing handball footage:

1. **Identify player position** relative to the goal they are attacking
2. **Estimate distance** from goal using court markings (6m D, 9m arc, center line)
3. **Assign zone number** based on lateral position (left/center/right) and depth (6m/9m/10m+)
4. **Track movements** by recording origin and destination zones

### Zone Assignment Rules
- If player is between two zones, choose the zone where their **body center** is located
- For **wing players** running along sidelines: use zones 2, 4, or 5 depending on depth
- For **pivots** moving along 6m line: primarily use zones 1-3
- For **back court players**: use zones 6-10 when positioned between 6m-9m lines
- For **deep/retreating players**: use zones 11-13 when beyond 9m

### Position Role Typical Zones
- **Goalkeeper (GK)**: Zone 0
- **Pivot (PV)**: Zones 2, 3, 4 (near 6m line, front of goal)
- **Left Wing (LW)**: Zones 1, 2, 6
- **Right Wing (RW)**: Zones 5, 4, 10
- **Left Back (LB)**: Zones 6, 7 (moves to adjacent)
- **Center Back (CB)**: Zones 7, 8, 9 (moves to adjacent)
- **Right Back (RB)**: Zones 9, 10 (moves to adjacent)

### **Role Dynamics**
- **Switching**: Back players often swap positions (crossing).
- **Visibility**: Beware of near-side wings being out of camera frame.

## Important Notes

⚠️ **Attacking Perspective**: Zones are always defined from the **attacking team's perspective**. When teams switch from attack to defense, the zone numbering remains relative to whichever team currently has possession.

🎯 **Approximate Locations**: These are coarse zones for strategic analysis, not precise coordinates. Estimate based on visible court markings.

📏 **Court Markings Reference**:
- 6m D-line: Semi-circular arc 6 meters from goal
- 9m line: Dashed arc 9 meters from goal (free throw line)
- Court dimensions: 40m x 20m (standard)
