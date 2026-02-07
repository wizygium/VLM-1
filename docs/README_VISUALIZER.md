# Handball Physics Visualizer

Interactive web-based visualization tool for handball physics analysis. View video side-by-side with real-time physics tracking on a 49-zone handball court.

## Features

- ✅ **S3 Video Streaming**: Stream videos directly from S3 (no download required)
- ✅ **49-Zone Court Visualization**: Interactive handball court with fine-grained spatial zones
- ✅ **Real-Time Sync**: Video playback synchronized with physics frames
- ✅ **Player Tracking**: Track IDs with jersey numbers and team colors
- ✅ **Event Detection**: Visual timeline of PASS and SHOT events
- ✅ **Frame-by-Frame Navigation**: Scrub through frames with keyboard shortcuts
- ✅ **Ball Possession**: Real-time ball state and holder tracking

## Quick Start

### 1. Start the Visualizer

```bash
./start_visualizer.sh
```

Or manually:

```bash
cd physics_visualizer
python server.py
```

### 2. Open in Browser

Navigate to: **http://127.0.0.1:8001**

### 3. Select Analysis

Use the dropdown to select from available physics analyses in `results_physics/`.

## Interface Overview

### Video Panel (Left)
- **Video Player**: Streams from S3 via presigned URLs
- **Playback Controls**: Play/pause, frame navigation, speed control
- **Keyboard Shortcuts**:
  - `Space`: Play/Pause
  - `←`: Previous frame
  - `→`: Next frame

### Court Visualization (Right)
- **49-Zone Grid**: Shows all zones (z0 goal + z1_1 through z6_8)
- **Player Markers**: Colored circles with jersey numbers
  - Blue circle = Blue team
  - White circle (gray border) = White team
  - Red border = Ball holder
- **Ball Indicator**: Gold circle when ball is loose/in-air
- **Zone Labels**: Sample zone identifiers for reference

### Timeline Scrubber
- Drag slider to navigate to specific frames
- Click events to jump to event timestamps
- Shows current time, total duration

### Events Panel
- **PASS Events**: Green cards showing pass details
  - From → To roles (CB → LB, etc.)
  - Zone movements
- **SHOT Events**: Red cards showing shot details
  - Shooter role/jersey
  - Origin zone
- **TURNOVER Events**: Orange cards showing possession loss
- **MOVE Events**: Blue cards showing significant tactical movement
- Click any event card to jump to that moment

### Players Panel
- Lists all tracked players with:
  - **Inferred Role** (LB, CB, PV, DL1...)
  - Track ID (t1, t2...)
  - Jersey number (#25, #12...)
  - Team color

## How It Works

### Data Flow

```
S3 Bucket → Presigned URL → Browser Video Player
                ↓
          Physics JSON → Frame Sync → Court Renderer
                ↓
          Events JSON → Timeline Markers
```

### Synchronization

The visualizer syncs video playback with physics frames:

1. **Video timeupdate event** → Find closest physics frame by timestamp
2. **Render frame** → Draw players and ball on court
3. **Update UI** → Display frame info, ball state, timeline position

### Court Rendering

The handball court uses a coordinate system:

```
Depth bands (6m-12m from goal):
  z6 (11-12m) - Top of court
  z5 (10-11m)
  z4 (9-10m)
  z3 (8-9m)
  z2 (7-8m)
  z1 (6-7m) - Near goal
  z0 - Goal zone

Lateral positions (left to right): 1, 2, 3, 4, 5, 6, 7, 8

Example: z3_4 = 8-9m depth, center position
```

## API Endpoints

The visualizer backend provides these REST endpoints:

### GET /api/analyses
List all available physics analyses

**Response:**
```json
{
  "analyses": [
    {
      "name": "ADF-Scene-001",
      "physics_file": "/path/to/physics.json",
      "events_file": "/path/to/events.json",
      "s3_uri": "s3://bucket/video.mp4",
      "total_frames": 24,
      "duration": 1.5,
      "unique_players": 13
    }
  ]
}
```

### GET /api/physics/{analysis_name}
Get physics data for specific analysis

**Response:** Full physics JSON with frames array

### GET /api/events/{analysis_name}
Get events data for specific analysis

**Response:** Events JSON with PASS/SHOT events

### GET /api/video-url/{analysis_name}
Generate presigned S3 URL for video streaming

**Query Parameters:**
- `expires_in`: URL expiration time in seconds (default: 3600)

**Response:**
```json
{
  "url": "https://s3.amazonaws.com/...",
  "expires_in": 3600
}
```

### GET /api/health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "s3_available": true,
  "results_dir": "results_physics",
  "results_dir_exists": true
}
```

## Configuration

### Results Directory

By default, the visualizer looks for physics results in:
```
/workspaces/VLM-1/results_physics/
```

To change this, edit `physics_visualizer/server.py`:

```python
RESULTS_DIR = Path("your/custom/path")
```

### Port

Default port is **8001**. To change:

```python
uvicorn.run(app, host="127.0.0.1", port=YOUR_PORT)
```

Or use environment variable:

```bash
export PORT=8002
python server.py
```

## Troubleshooting

### "No analyses available"

**Cause:** No physics JSON files found in results directory

**Solution:**
```bash
# Process a video first
./process_s3_handball.sh s3://your-bucket/video.mp4

# Or check results directory
ls -la results_physics/
```

### "Failed to load video"

**Cause:** S3 presigned URL expired or AWS credentials issue

**Solutions:**
1. Refresh the page to generate new presigned URL
2. Check AWS credentials: `aws s3 ls`
3. Verify S3 bucket permissions

### "Video and court not syncing"

**Cause:** Timestamp mismatch between video and physics frames

**Solution:** Physics analyzer outputs actual video timestamps, not perfect 16fps intervals. This is normal - the sync algorithm finds the closest frame.

### Court rendering looks wrong

**Cause:** Canvas size or zone coordinate calculation issue

**Solution:**
1. Check browser console for errors
2. Try resizing browser window
3. Hard refresh: Ctrl+Shift+R (Windows) / Cmd+Shift+R (Mac)

## Development

### File Structure

```
physics_visualizer/
├── server.py              # FastAPI backend
└── static/
    ├── index.html        # Main HTML page
    ├── style.css         # Styles
    ├── app.js            # Main application logic
    └── court-renderer.js # Court visualization module
```

### Adding Features

**To add a new visualization element:**

1. Edit `court-renderer.js` → Add drawing method
2. Edit `app.js` → Call method in `renderCurrentFrame()`
3. Update CSS in `style.css` if needed

**To add a new API endpoint:**

1. Edit `server.py` → Add `@app.get()` or `@app.post()` route
2. Update `app.js` → Call new endpoint with `fetch()`

### Hot Reload

For development with auto-reload:

```bash
cd physics_visualizer
uvicorn server:app --reload --host 127.0.0.1 --port 8001
```

## Performance

### Typical Metrics

- **Video Loading**: 2-3 seconds (presigned URL generation)
- **Physics Data**: < 1 second (13KB JSON for 24 frames)
- **Frame Rendering**: < 16ms (60fps capable)
- **Scrubber Response**: Instant (pre-loaded data)

### Optimization Tips

1. **Reduce canvas size** for slower devices:
   ```javascript
   <canvas id="court-canvas" width="400" height="600"></canvas>
   ```

2. **Limit displayed players** if tracking many:
   ```javascript
   // Only show players near ball
   const nearbyPlayers = players.filter(p => isNearBall(p, ball));
   ```

3. **Cache S3 URLs** to reduce API calls (already implemented with 1-hour TTL)

## Credits

Built with:
- **FastAPI** - Backend API framework
- **boto3** - AWS S3 integration
- **HTML5 Canvas** - Court rendering
- **Vanilla JavaScript** - No frameworks, maximum performance

## See Also

- [README_PHYSICS_ANALYZER.md](README_PHYSICS_ANALYZER.md) - Physics analysis pipeline
- [README_S3_INTEGRATION.md](README_S3_INTEGRATION.md) - S3 streaming details
- [CLAUDE.md](CLAUDE.md) - Project overview and commands
