# Quick Start: Physics Visualizer

## Start the Server
```bash
cd physics_visualizer && python server.py
# Open http://127.0.0.1:8001
```

Or with the virtual environment:
```bash
.venv/bin/python3 physics_visualizer/server.py
```

## What You'll See

The visualizer has three panels:
1. **Video** (left): Synced video playback from local files or S3
2. **Court Simulation** (center): 14-zone handball court with player markers
3. **Timeline** (right): Unified timeline of physics frames and inferred events

### Timeline Features
- **Physics frame cards**: Show ball state, holder, zone, and transition chips (catch/release/transfer/zone-change)
- **Inferred event cards**: PASS, SHOT, MOVE, TURNOVER with from/to details
- **Filter bar**: All / Changes only / Events only
- **Auto-scroll**: Active frame stays visible during playback

## Check Server Health
```bash
curl http://127.0.0.1:8001/api/health
```

## Check Available Analyses
```bash
curl http://127.0.0.1:8001/api/analyses
```

The server scans `data/analyses/` for `*_physics.json` and `*_events.json` files.

## Common Issues

### Port Already in Use
```bash
lsof -i :8001
kill -9 <PID>
```

### Missing Dependencies
```bash
pip install fastapi uvicorn boto3
```

### Video Won't Load
- The server first checks for local video files in `data/videos/`
- If not found, it tries S3 presigned URLs (requires AWS credentials)
- If neither available, the UI still loads with court and timeline — video panel shows placeholder

### Browser Shows Stale UI
Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows/Linux)

## Verification Checklist

After loading an analysis:
- Video player appears (or placeholder if no video)
- 14-zone court renders with curved D-lines
- Players shown as coloured circles with track IDs
- Ball holder has red border highlight
- Timeline shows physics frames and events
- Scrubbing the video updates court and timeline
- Clicking a timeline card seeks the video to that timestamp
