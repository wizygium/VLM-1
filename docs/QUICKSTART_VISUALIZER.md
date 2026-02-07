# Quick Start Guide - Physics Visualizer

## Issue: Can't Load Page

If you can't load the visualization page at http://127.0.0.1:8001, follow these steps:

### Step 1: Check if Server is Running

Open a terminal and run:
```bash
lsof -i :8001
```

**If you see output**: The server is running. Skip to Step 3.
**If no output**: The server is not running. Continue to Step 2.

### Step 2: Start the Server

Open a terminal in the project directory and run:

```bash
cd /workspaces/VLM-1
./start_visualizer.sh
```

Or manually:
```bash
cd /workspaces/VLM-1/physics_visualizer
python3 server.py
```

You should see output like:
```
============================================================
Handball Physics Visualizer
============================================================
Results directory: /workspaces/VLM-1/results_physics
S3 client available: True

Starting server at http://127.0.0.1:8001
============================================================
INFO:     Started server process [...]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8001
```

### Step 3: Test the Server

In another terminal, test if the server is responding:

```bash
curl http://127.0.0.1:8001/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "s3_available": true,
  "results_dir": "/workspaces/VLM-1/results_physics",
  "results_dir_exists": true
}
```

### Step 4: Test Available Analyses

```bash
curl http://127.0.0.1:8001/api/analyses
```

Should return:
```json
{
  "analyses": [
    {
      "name": "ADF-Scene-001",
      "physics_file": "/workspaces/VLM-1/results_physics/ADF-Scene-001_physics.json",
      "events_file": "/workspaces/VLM-1/results_physics/ADF-Scene-001_events.json",
      "s3_uri": "s3://...",
      "total_frames": 24,
      "duration": 1.5,
      "unique_players": 12
    }
  ]
}
```

### Step 5: Open in Browser

Open your browser and navigate to:
```
http://127.0.0.1:8001
```

OR use VS Code's Simple Browser:
- Press `Ctrl+Shift+P` (Cmd+Shift+P on Mac)
- Type "Simple Browser"
- Select "Simple Browser: Show"
- Enter URL: `http://127.0.0.1:8001`

### Step 6: Test the UI

1. **Select Analysis**: Choose "ADF-Scene-001" from dropdown
2. **Check Browser Console**: Press F12 to open DevTools
3. **Look for Errors**: Check the Console tab for any red errors

## Common Issues

### Issue: Port Already in Use

```bash
# Find and kill the process
lsof -i :8001
kill -9 <PID>

# Or kill all python processes on that port
pkill -f "python.*server.py"
```

### Issue: Module Import Errors

```bash
# Install missing dependencies
pip install fastapi uvicorn boto3
```

### Issue: S3 Video Won't Load

```bash
# Configure AWS credentials
aws configure

# Test S3 access
aws s3 ls s3://sagemaker-us-east-1-086355358526/data/raw_scenes/ADF/
```

### Issue: Blank Court or No Players Rendering

This was **FIXED** in the recent update. Make sure you:
1. Hard refresh browser: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
2. Clear browser cache
3. The fix corrected inverted zone coordinates

## Verification Steps

After loading an analysis, verify:

✅ Video player appears and loads  
✅ Court grid displays with 49 zones  
✅ Players render as colored circles with jersey numbers  
✅ Blue team shows as blue circles  
✅ White team shows as white/gray circles  
✅ Ball holder has red border  
✅ Events list shows on the right  
✅ Timeline scrubber works  

## Manual Server Start (Detailed)

If the script doesn't work, start manually:

```bash
# Navigate to visualizer directory
cd /workspaces/VLM-1/physics_visualizer

# Start Python server
python3 server.py
```

Keep this terminal open. The server will run and show logs.

In another terminal or browser, access: http://127.0.0.1:8001

## Debugging Commands

```bash
# Check all dependencies
python3 -c "import fastapi, uvicorn, boto3; print('All OK')"

# Check results directory
ls -lh /workspaces/VLM-1/results_physics/

# View physics JSON
cat /workspaces/VLM-1/results_physics/ADF-Scene-001_physics.json | python3 -m json.tool | head -50

# Test server endpoint directly
curl -v http://127.0.0.1:8001/

# Check static files
ls -lh /workspaces/VLM-1/physics_visualizer/static/
```

## What Was Fixed

**Bug**: Zone coordinates were inverted (players rendering upside-down on court)
**Fix**: Corrected y-coordinate calculation in `court-renderer.js`
**Status**: ✅ Fixed (2026-01-31)

See `VISUALIZATION_FIXES.md` for details.

## Need Help?

1. Check `DEBUG_VISUALIZER.md` for comprehensive debugging guide
2. Check `README_VISUALIZER.md` for feature documentation
3. Ensure you've refreshed the browser after the fix

---

**Quick Command Reference:**

```bash
# Start server
cd /workspaces/VLM-1 && ./start_visualizer.sh

# Test health
curl http://127.0.0.1:8001/api/health

# Check port
lsof -i :8001

# Kill server
pkill -f "python.*physics_visualizer"
```
