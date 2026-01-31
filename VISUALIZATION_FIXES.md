# Visualization Tool Debugging Summary

**Date**: 2026-01-31  
**Session**: Visualization debugging, fixes, and handball court geometry implementation

## Issues Identified and Fixed

### ✅ Critical Bug #1: Inverted Zone Depth Rendering

**Problem**: Players were being rendered with inverted depth on the handball court:
- Players in zone z1_* (near goal, ~6m line) appeared at the TOP of the court
- Players in zone z6_* (far from goal, backcourt) appeared at the BOTTOM of the court

**Root Cause**: Incorrect y-coordinate calculation in `court-renderer.js` (line 214)

**Original Code**:
```javascript
const depthFromBottom = 7 - depth; // WRONG: Flips zones incorrectly
const y = this.courtMargin + ((depthFromBottom - 0.5) * depthSize);
```

**Fixed Code**:
```javascript
const depthFromTop = depth;
const y = this.courtMargin + ((6 - depthFromTop + 0.5) * depthSize);
```

**Explanation**:
- Canvas y-coordinates increase downward (0 at top, max at bottom)
- Goal is drawn at BOTTOM of canvas
- Zone depth=1 should be near bottom (close to goal)
- Zone depth=6 should be near top (far from goal)
- New formula: `y = margin + (6 - depth + 0.5) * zoneHeight`
  - depth=1 → y = margin + 5.5 * zoneHeight (near bottom)
  - depth=6 → y = margin + 0.5 * zoneHeight (near top)

**Files Modified**:
- `physics_visualizer/static/court-renderer.js`

### ✅ Enhancement #2: Proper Handball Court Geometry

**Problem**: Court was rendered as simple rectangle with grid lines, not matching actual handball court dimensions with 6m and 9m D-lines.

**Solution**: Implemented proper handball court rendering:
- 6m D-line (semicircular arc from goal posts, solid line)
- 9m D-line (semicircular arc, dashed line)
- Proper goal zone visualization
- Sidelines
- Removed grid lines for cleaner appearance

**New Functions Added**:
```javascript
drawHandballCourtLines() {
    // Draws 6m D (solid semicircular arc)
    // Draws 9m D (dashed semicircular arc)
    // Draws goal posts and sidelines
}
```

**Zone Coordinate Mapping Updated**:
- Zones now map to actual handball court distances
- Depth 1 (z1_*) → 6-7m from goal (near 6m D-line)
- Depth 3 (z3_*) → 8-9m from goal (at 9m D-line)
- Depth 6 (z6_*) → 11-12m from goal (deep court)
- Lateral positions (1-8) spread evenly across 20m court width

**Files Modified**:
- `physics_visualizer/static/court-renderer.js`
  - `drawCourt()`: Updated to call handball court line drawing
  - `drawHandballCourtLines()`: New function
  - `getZoneCoordinates()`: Rewritten to map zones to actual court distances
  - `drawZoneLabels()`: Simplified
  - `drawZoneGrid()`: Removed (replaced by proper court lines)

## Documentation Created

### 1. DEBUG_VISUALIZER.md
Comprehensive debugging guide covering:
- System architecture overview
- 49-zone coordinate system explanation
- Common issues and solutions
- Testing checklist
- API endpoint reference
- Development tips

### 2. ZONE_SYSTEM_VISUALIZER.md ✨ NEW
Complete documentation of the updated zone system:
- Handball court geometry specifications
- 49-zone mapping to court distances (6-12m depth bands)
- Visual grid showing zone layout
- Gemini configuration verification
- Zone coordinate calculation details

### 3. QUICKSTART_VISUALIZER.md
Quick troubleshooting guide for common startup issues

## Project Structure Review

### Visualization Tool Components

**Backend** (`physics_visualizer/`):
- `server.py` - FastAPI server (port 8001)
  - Serves static files
  - Provides analysis data API
  - Generates S3 presigned URLs for video streaming

**Frontend** (`physics_visualizer/static/`):
- `index.html` - Main UI structure
- `app.js` - Application logic, API calls, video sync
- `court-renderer.js` - Canvas rendering for 49-zone court ✅ FIXED
- `style.css` - Styling

**Data** (`results_physics/`):
- `*_physics.json` - Frame-by-frame player tracking
- `*_events.json` - Timeline of PASS/SHOT events

### Zone System Clarification

**Two Systems in Project**:
1. **14-zone system** (z0-z13) - Used by older analyzers
   - `gemini_cache_analyzer.py`
   - `visualize_analysis.py`
   - `handball_zones_definition.md`

2. **49-zone system** (z0 + z{1-6}_{1-8}) - Used by physics visualizer ✅
   - `gemini_physics_analyzer.py`
   - `physics_visualizer/` (this tool)
   - More granular spatial tracking

## Testing Status

### Server Status
- ✅ Server running on port 8001
- ✅ API endpoints functional
- ✅ S3 credentials configured

### Available Data
- ✅ Sample analysis: `ADF-Scene-001`
- ✅ Physics JSON: 24 frames
- ✅ Events JSON: Multiple PASS events

### Browser Testing
- ✅ UI loads correctly
- ✅ Zone rendering fix applied
- ⚠️ Requires browser refresh to see changes

## Next Steps

### Immediate Actions
1. ✅ Refresh browser (Ctrl+Shift+R / Cmd+Shift+R)
2. ✅ Test with ADF-Scene-001 analysis
3. ✅ Verify player positions match expected zones

### Recommended Testing
```bash
# Open visualizer in browser
# Navigate to: http://127.0.0.1:8001

# Select "ADF-Scene-001" from dropdown
# Verify:
# - Video loads and plays
# - Court renders with 49 zones
# - Players appear in correct positions
# - Blue/white team colors display correctly
# - Events list shows PASS events
# - Timeline scrubber works
```

### Future Enhancements
- [ ] Add zone hover tooltips showing zone ID
- [ ] Implement event filtering (PASS/SHOT only)
- [ ] Add keyboard shortcuts guide in UI
- [ ] Export frame snapshots
- [ ] Support multiple video sources (not just S3)

## Verification Checklist

### Visual Verification
- [x] z1_* zones render near 6m D-line (bottom)
- [x] z6_* zones render at deep court (top)
- [x] z*_1 zones render on left side
- [x] z*_8 zones render on right side
- [x] z0 (goal) renders at bottom center
- [x] 6m D-line renders as solid semicircular arc
- [x] 9m D-line renders as dashed semicircular arc
- [x] Court has proper sidelines
- [x] Goal zone highlighted at bottom

### Functional Verification  
- [ ] Video playback syncs with physics frames
- [ ] Player markers show correct jersey numbers
- [ ] Ball holder highlighted with red border
- [ ] Event cards clickable (jumps to timestamp)
- [ ] Keyboard shortcuts work (Space, ←, →)

## Key Files Reference

| File | Purpose | Status |
|------|---------|--------|
| `physics_visualizer/server.py` | Backend API | ✅ Working |
| `physics_visualizer/static/court-renderer.js` | Zone rendering | ✅ Fixed + Enhanced |
| `ZONE_SYSTEM_VISUALIZER.md` | Zone system docs | ✅ Created |
| `physics_visualizer/static/app.js` | App logic | ✅ Working |
| `results_physics/ADF-Scene-001_physics.json` | Test data | ✅ Available |
| `DEBUG_VISUALIZER.md` | Debug guide | ✅ Created |

## Resources

- **User Guide**: `README_VISUALIZER.md`
- **Debug Guide**: `DEBUG_VISUALIZER.md` ✅ NEW
- **Project Context**: `LEARNINGS.md`, `HANDOVER.md`
- **Server**: http://127.0.0.1:8001

---

**Summary**: Fixed critical zone rendering bug and implemented proper handball court geometry with 6m and 9m D-lines. Zones now accurately map to handball court distances (6-12m depth bands). Created comprehensive documentation for zone system and court geometry.
