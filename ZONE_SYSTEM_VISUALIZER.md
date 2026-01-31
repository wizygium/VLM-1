# Physics Visualizer Zone System - Updated

## Overview
The physics visualizer now uses **proper handball court geometry** with 6m and 9m D-lines (semicircular arcs). The 49-zone system maps to actual handball court distances.

## Handball Court Dimensions

### Standard Court (Regulation)
- **Width**: 20 meters
- **Length**: 40 meters (showing 20m attacking half)
- **Goal**: 3 meters wide, 2 meters high

### Key Lines
- **6m D-line** (Goal Area Line): 
  - Two 6-meter radius arcs centered at each goal post
  - Connected by 3m straight line at the top (parallel to goal line)
  - Solid line
- **9m D-line** (Free Throw Line):
  - Two 9-meter radius arcs centered at each goal post
  - Connected by 3m dashed line at the top
  - Ends where it intersects the sidelines
  - Dashed line
- **Halfway line**: 20 meters from goal line
- **Sidelines**: Court boundaries (20m wide)

## 49-Zone Mapping to Court Geometry

### Zone Structure
- **z0**: Goal zone (goalkeeper area)
- **z{depth}_{lateral}**: Playing area zones
  - **depth** (1-6): Distance bands from goal
  - **lateral** (1-8): Left-to-right position

### Depth Bands (Distance from Goal Line)

| Depth | Distance | Court Area | Visual Reference |
|-------|----------|------------|------------------|
| 1 | 6-7m | Just beyond 6m D-line | Wing/pivot area (6.5m center) |
| 2 | 7-8m | Between 6m and 9m | Near backcourt (7.5m center) |
| 3 | 8-9m | At/around 9m D-line | Backcourt line (8.5m center) |
| 4 | 9-10m | Just beyond 9m | Deep backcourt (9.5m center) |
| 5 | 10-11m | Far backcourt | Transition area (10.5m center) |
| 6 | 11-12m | Very deep | Near center line (11.5m center) |

### Lateral Positions (Left to Right)

| Lateral | Position | Description |
|---------|----------|-------------|
| 1 | Far left | Left wing area |
| 2-3 | Left-center | Left back area |
| 4-5 | Center | Central playmaker area |
| 6-7 | Right-center | Right back area |
| 8 | Far right | Right wing area |

## Visual Grid

```
                ATTACKING DIRECTION ↑
                                    
Depth 6 (11-12m): z6_1  z6_2  z6_3  z6_4  z6_5  z6_6  z6_7  z6_8
                  [-------- Deep Backcourt --------]

Depth 5 (10-11m): z5_1  z5_2  z5_3  z5_4  z5_5  z5_6  z5_7  z5_8
                  [-------- Far Backcourt ---------]

Depth 4 (9-10m):  z4_1  z4_2  z4_3  z4_4  z4_5  z4_6  z4_7  z4_8
                  [-- Just Beyond 9m D-line ----]

        ╭─────────── 9m D-line (dashed) ───────────╮
        
Depth 3 (8-9m):   z3_1  z3_2  z3_3  z3_4  z3_5  z3_6  z3_7  z3_8
                  [---- Backcourt (on 9m) -------]

Depth 2 (7-8m):   z2_1  z2_2  z2_3  z2_4  z2_5  z2_6  z2_7  z2_8
                  [--- Between 6m and 9m -------]

        ╭─────────── 6m D-line (solid) ────────────╮

Depth 1 (6-7m):   z1_1  z1_2  z1_3  z1_4  z1_5  z1_6  z1_7  z1_8
                  [---- Wing/Pivot Area --------]

                  ╰────────── GOAL (z0) ──────────╯
                            (3m wide)

Lateral:          1     2     3     4     5     6     7     8
                (Left) <------- Center -------> (Right)
```

## Gemini Zone Recognition

### System Instruction (physics_prompt.md)
Gemini is already correctly configured with this zone system:

```markdown
Depth from goal line:
- Depth 1: 6m-7m
- Depth 2: 7m-8m
- Depth 3: 8m-9m
- Depth 4: 9m-10m
- Depth 5: 10m-11m
- Depth 6: 11m-12m

Lateral position (left to right from attacker's view):
- 1 = Far left
- 2-3 = Left-center
- 4-5 = Center
- 6-7 = Right-center
- 8 = Far right
```

**Status**: ✅ Gemini prompt already matches visualizer zone system

## Visualization Updates

### What Changed (Latest)
1. **Court rendering**: Corrected handball court geometry
   - 6m D-line: Two 6m radius arcs from goal posts + 3m straight line
   - 9m D-line: Two 9m radius arcs from goal posts + 3m dashed line
   - Halfway line at 20m from goal
   - Proper scaling: 20m court width → canvas width
2. **Zone coordinates**: Fixed to use meters-to-pixels conversion
   - depth 1 @ 6.5m, depth 2 @ 7.5m, depth 3 @ 8.5m, etc.
   - Lateral zones evenly distributed across 20m width
3. **Zone labels**: Updated to show depth markers and lateral numbers

### Coordinate Calculation
```javascript
// Court scale: 20m width maps to canvas width
const metersToPixels = this.courtWidth / 20;

// Zone depth positioning (center of each meter band)
const depthMeters = 6 + depth - 0.5; // depth 1 = 6.5m, depth 6 = 11.5m
const y = goalY - (depthMeters * metersToPixels);

// Lateral positioning (8 equal bands across 20m)
const lateralSize = this.courtWidth / 8;
const x = this.courtMargin + ((lateral - 0.5) * lateralSize);
```

## Example Zone Positions

### Typical Offensive Formation
- **z1_1, z1_8**: Wings at 6m line (far left/right)
- **z1_4, z1_5**: Pivot at 6m line (center)
- **z3_2, z3_7**: Left/right backs at 9m line
- **z3_4, z3_5**: Center back/playmaker at 9m line

### Defensive Positioning
- **z0**: Goalkeeper
- **z1_1 to z1_8**: 6-0 defense along 6m line
- **z3_4, z3_5**: Advanced defender in 5-1 formation (at 9m)

## Verification

### Visual Checks
✅ 6m D-line: Two 6m radius arcs from goal posts + 3m straight line (solid)  
✅ 9m D-line: Two 9m radius arcs from goal posts + 3m straight line (dashed)  
✅ Halfway line at 20m from goal  
✅ Goal zone (z0) at bottom center (3m wide)  
✅ Depth 1 zones at ~6.5m from goal  
✅ Depth 3 zones at ~8.5m from goal (near 9m line)  
✅ Depth 6 zones at ~11.5m from goal  
✅ Lateral zones spread evenly across 20m width (8 equal bands)  
✅ Proper meters-to-pixels scaling  

### Test with Sample Data
Using `ADF-Scene-001_physics.json`:
- Players in z3_2, z3_3 → Should render near 9m line, left-center
- Players in z1_4 → Should render near 6m line, center
- Ball in z3_4 → Should render at 9m line, center

## Next Steps

### If Gemini Needs Adjustment
The current `physics_prompt.md` already specifies:
- Depth bands with meter ranges (6-7m, 7-8m, etc.)
- Lateral positions (1=left, 8=right)
- Visual grid showing zone layout

**No changes needed to Gemini configuration** - it already recognizes zones correctly.

### If Rendering Looks Wrong
1. Check depth calculation in `getZoneCoordinates()`
2. Verify 6m/9m D-line rendering positions
3. Test with known player positions from physics JSON

## Files Modified

- `physics_visualizer/static/court-renderer.js`:
  - `drawCourt()`: Added handball court line rendering
  - `drawHandballCourtLines()`: New function for 6m/9m D-lines
  - `getZoneCoordinates()`: Updated to map zones to actual court distances
  - `drawZoneLabels()`: Simplified labels

## References

- **Physics Prompt**: `physics_prompt.md` (Gemini instructions)
- **Old Visualizer**: `visualize_analysis.py` (handball court drawing reference)
- **Physics Analyzer**: `gemini_physics_analyzer.py` (zone system usage)

---

**Last Updated**: 2026-01-31  
**Status**: Handball court geometry implemented  
**Compatibility**: Matches Gemini physics prompt zone definitions
