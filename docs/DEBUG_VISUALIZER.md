# Physics Visualizer Debugging Guide

## Overview
The Handball Physics Visualizer is a web-based tool for viewing handball physics analysis side-by-side with video playback. This document covers common issues and debugging steps.

## System Architecture

### Components
1. **Backend Server** (`physics_visualizer/server.py`)
   - FastAPI server running on port 8001
   - Serves static files (HTML, CSS, JS)
   - Provides API endpoints for data and S3 video URLs
   
2. **Frontend** (`physics_visualizer/static/`)
   - `index.html` - Main UI structure
   - `app.js` - Application logic and API calls
   - `court-renderer.js` - Canvas rendering for 49-zone court
   - `style.css` - Styling

3. **Data** (`results_physics/`)
   - `*_physics.json` - Frame-by-frame tracking data
   - `*_events.json` - Event timeline (PASS, SHOT, etc.)

## Zone System

### 49-Zone Layout
The court uses a **49-zone grid system**:
- **Zone 0**: Goal area (goalkeeper position)
- **Zones z{1-6}_{1-8}**: Playing area
  - **Depth bands** (1-6): Distance from goal
    - `1` = Closest to goal (~6m line)
    - `6` = Farthest from goal (~midfield)
  - **Lateral zones** (1-8): Left-to-right position
    - `1` = Far left
    - `4-5` = Center
    - `8` = Far right

### Coordinate System
- **Canvas origin**: Top-left (0, 0)
- **Goal location**: Bottom of canvas
- **Y-axis**: Increases downward (top to bottom)
- **Depth mapping**:
  - depth=6 → Top of playing area (farthest from goal)
  - depth=1 → Bottom of playing area (closest to goal)

## Recent Fixes

### Bug #1: Inverted Zone Depth Rendering ✅ FIXED
**Issue**: Players were being rendered in inverted depth positions.
- z1_4 (near goal) was showing at top of court
- z6_4 (far from goal) was showing at bottom of court

**Root Cause**: Incorrect coordinate calculation in `court-renderer.js` line 214:
```javascript
// WRONG:
const depthFromBottom = 7 - depth;
```

**Fix Applied**: Corrected the y-coordinate calculation:
```javascript
// CORRECT:
const depthFromTop = depth;
const y = this.courtMargin + ((6 - depthFromTop + 0.5) * depthSize);
```

**Verification**: 
- z1_4 should render near goal (bottom)
- z6_4 should render far from goal (top)

## Testing Checklist

### 1. Server Status
```bash
# Check if server is running
lsof -i :8001

# View server logs (if running in foreground)
# Look for errors in S3 authentication, file loading, etc.
```

### 2. Available Analyses
```bash
# Test API endpoint
curl http://127.0.0.1:8001/api/analyses

# Should return JSON with available analyses
```

### 3. S3 Video Access
**Common Issue**: AWS credentials not configured
```bash
# Configure AWS CLI
aws configure

# Test S3 access
aws s3 ls s3://sagemaker-us-east-1-086355358526/data/raw_scenes/
```

### 4. Browser Console
Open DevTools (F12) and check for:
- JavaScript errors
- Failed network requests (API calls, S3 URLs)
- Console warnings

### 5. Zone Rendering Test
Manually verify zone positions:
1. Load an analysis
2. Pause on a frame with visible players
3. Check player positions match expected zones:
   - Low jersey numbers (near 6m line) should be near bottom
   - High depth zones (backcourt players) should be near top

## Common Issues

### Issue: "Failed to load video"
**Causes**:
1. S3 credentials not configured
2. Invalid S3 URI in physics JSON
3. Network connectivity issues

**Solutions**:
```bash
# 1. Configure AWS credentials
aws configure

# 2. Verify S3 URI format
# Should be: s3://bucket-name/path/to/video.mp4

# 3. Test S3 access directly
aws s3 ls s3://sagemaker-us-east-1-086355358526/data/raw_scenes/ADF/
```

### Issue: "No analyses available"
**Causes**:
1. `results_physics/` directory empty
2. Physics JSON files malformed

**Solutions**:
```bash
# Check directory contents
ls -la results_physics/

# Validate JSON files
python -m json.tool results_physics/ADF-Scene-001_physics.json
```

### Issue: Players not rendering or in wrong positions
**Causes**:
1. Invalid zone format (must be "z0" or "z{1-6}_{1-8}")
2. Coordinate calculation bugs
3. Missing player data

**Solutions**:
1. Check physics JSON format:
```json
{
  "players": [
    {
      "track_id": "t1",
      "zone": "z3_4",  // Must be string format
      "jersey_number": "25",
      "team": "blue"
    }
  ]
}
```

2. Verify zone validation in `court-renderer.js`:
   - Depth must be 1-6
   - Lateral must be 1-8

### Issue: Video and court out of sync
**Causes**:
1. Frame timestamps don't match video time
2. Video playback rate changed

**Solutions**:
1. Check `metadata.fps` in physics JSON
2. Verify frame timestamps are sequential
3. Use video controls to manually sync

## Development Tips

### Testing Zone Coordinates
Add debug logging to `court-renderer.js`:
```javascript
getZoneCoordinates(zone) {
    // ... existing code ...
    console.log(`Zone ${zone} -> (${x}, ${y})`);
    return { x, y };
}
```

### Simulating Data
Create minimal test JSON:
```json
{
  "video": "s3://bucket/video.mp4",
  "metadata": {
    "fps": 16.0,
    "total_frames": 10
  },
  "frames": [
    {
      "timestamp": "0.063",
      "ball": {
        "holder_track_id": "t1",
        "zone": "z3_4",
        "state": "Holding"
      },
      "players": [
        {
          "track_id": "t1",
          "zone": "z3_4",
          "jersey_number": "14",
          "team": "blue"
        }
      ]
    }
  ]
}
```

### Hot Reloading
For development:
1. Make changes to static files (JS, CSS, HTML)
2. Hard refresh browser (Ctrl+Shift+R / Cmd+Shift+R)
3. Server restart not needed for static file changes

## API Endpoints Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve main HTML page |
| `/api/analyses` | GET | List available analyses |
| `/api/physics/{name}` | GET | Get physics JSON data |
| `/api/events/{name}` | GET | Get events JSON data |
| `/api/video-url/{name}` | GET | Generate S3 presigned URL |
| `/api/health` | GET | Health check |

## Related Documentation

- `README_VISUALIZER.md` - User guide and feature overview
- `README_PHYSICS_ANALYZER.md` - How physics analysis is generated
- `handball_zones_definition.md` - Legacy 14-zone system (not used here)
- `gemini_physics_analyzer.py` - Physics analysis generator

## Next Steps

### Planned Improvements
- [ ] Add zone hover tooltips
- [ ] Event filtering (show only PASS or SHOT)
- [ ] Export frames as images
- [ ] Playback speed presets (0.25x, 0.5x, 1x, 2x)
- [ ] Multiple camera angles (if available)

### Known Limitations
1. Only supports 49-zone system (not compatible with 14-zone legacy data)
2. Requires S3 access for video streaming
3. No offline mode (videos must be in S3)
4. Limited to handball court dimensions

## Troubleshooting Commands

```bash
# Kill existing server
pkill -f "python.*physics_visualizer/server.py"

# Start fresh
cd /workspaces/VLM-1
./start_visualizer.sh

# Check server logs
tail -f physics_visualizer/server.log  # If logging enabled

# Test API locally
curl http://127.0.0.1:8001/api/health
curl http://127.0.0.1:8001/api/analyses

# View browser with server logs
# Open http://127.0.0.1:8001 and check DevTools Console
```

## Contact & Support

For issues or questions:
1. Check this debugging guide
2. Review `LEARNINGS.md` for project context
3. Check `HANDOVER.md` for overall project status

---

**Last Updated**: 2026-01-31  
**Version**: 1.0  
**Status**: Active Development
