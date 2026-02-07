import os
import json
import math
import cv2
import asyncio
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import subprocess
import time
from fastapi.responses import FileResponse

# Import from the existing logic
from analyze_handball import VideoProcessor, extract_json, create_frame_grid

app = FastAPI()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.mount("/data", StaticFiles(directory=str(DATA_DIR)), name="data")

# Global state for tasks
jobs = {}
# Global processor to avoid reloading model
processor = None

class AnalysisRequest(BaseModel):
    video_path: str
    context_path: Optional[str] = None
    batch_size: int = 20
    fps: float = 1.5
    start_offset: float = 0.0
    num_frames: int = 6

@app.get("/")
def read_root():
    return FileResponse(BASE_DIR / "static" / "index.html")

def extract_clip(video_path: str, start_time: float, output_path: str, duration: float = 0.5):
    """Extract a small clip using ffmpeg, centered on the start_time."""
    ss = max(0, start_time - 0.25)
    cmd = [
        "ffmpeg", "-y", "-nostdin", "-hide_banner", "-loglevel", "error",
        "-ss", str(ss),
        "-i", video_path,
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "28",
        "-an",
        output_path
    ]
    subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True)

def run_analysis_task(job_id: str, req: AnalysisRequest):
    global processor
    print(f"Starting job {job_id}...")
    try:
        if processor is None:
            print("Loading VLM model for the first time...")
            jobs[job_id]["status"] = "Loading model..."
            processor = VideoProcessor()
        
        ctx_data = {}
        if req.context_path and os.path.exists(req.context_path):
            with open(req.context_path, 'r') as f:
                ctx_data = json.load(f)

        jobs[job_id]["status"] = "Extracting frames..."
        
        # Open video and get properties
        cap = cv2.VideoCapture(str(req.video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        total_duration = total_frames / fps if fps > 0 else 0
        cap.release()

        # Calculate interval
        remaining_duration = max(0, total_duration - req.start_offset)
        interval = remaining_duration / req.num_frames if req.num_frames > 1 else 1.0
        
        # Use processor to extract
        frames_all = processor.extract_frames(req.video_path, interval_seconds=interval)
        
        # Filter and limit
        frames = [(ts, img) for ts, img in frames_all if ts >= req.start_offset - 0.1]
        frames = frames[:req.num_frames]
        
        job_dir = DATA_DIR / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        
        analysis_results = []
        
        # Teams context
        teams = ctx_data.get("teams", [])
        team_context = ", ".join([f"{t['color']} jersey = {t['name']}" for t in teams]) if teams else "WHITE = ATTACK, BLACK = DEFENSE"
        match_info = f"MATCH: {ctx_data.get('match', '')}" if ctx_data.get('match') else ""

        num_batches = math.ceil(len(frames) / req.batch_size)
        previous_batch_json = ""

        for b_idx in range(num_batches):
            batch_start = b_idx * req.batch_size
            batch = frames[batch_start : batch_start + req.batch_size]
            batch_images_bytes = [img_bytes for _, img_bytes in batch]
            duration = batch[-1][0] - batch[0][0] if len(batch) > 1 else 0
            
            # Memory and Rules
            memory_context = f"\n### PREVIOUS CONTEXT:\n{previous_batch_json}\nMaintain continuity." if previous_batch_json else ""

            temporal_prompt = f"""These {len(batch)} images form a chronological sequence covering {duration:.2f} seconds.
{match_info}
Teams: {team_context}

### HANDBALL LOGIC & RULES (STRICT ENFORCEMENT):

1. **PLAYER ROLES:** Identify players by their position on court:
   - **GK (Goalkeeper):** In goal area.
   - **LW/RW (Wingers):** Far left/right corners.
   - **LB/RB (Backs):** 9m line left/right.
   - **CB (Center Back):** Middle 9m.
   - **PV (Pivot):** Inside 6m line among defenders.

2. **PASSING LOGIC (CRITICAL):**
   - Passes are almost ALWAYS between **TEAMMATES** (Same Jersey Color).
   - Example: WHITE Player -> WHITE Player.
   - INTERCEPTIONS (Opposite Team) are rare events. Only label if clearly visible.

3. **POSSESSION STATE:**
   - DRIBBLING: Only label if hand is pushing ball to floor.
   - HOLDING: Player gripping ball.
   - NO POSSESSION: Ball is in air (Pass/Shot).

4. **SHOT OUTCOMES:**
   - **GOAL:** Ball fully crosses line. net movement.
   - **SAVE:** GK blocks ball.
   - **MISS:** Ball goes wide/high.
   - **POST/BAR:** Ball hits frame.


Analyze the frames in this sequence:
Return a JSON ARRAY with EXACTLY {len(batch)} objects, one per frame shown in the grid.
Each object should have this EXACT structure (no other text):
{{
  "frame": {{
    "time": "X.XX seconds",
    "possession": {{
      "team": "WHITE/BLACK/NONE",
      "player_role": "LB/RB/CB/PV/LW/RW/GK",
      "action": "Dribble/Hold/Pass/Shot"
    }},
    "event": {{
      "type": "PASS/SHOT/TURNOVER/NONE",
      "from_role": "Role (e.g. RB)",
      "to_role": "Role (e.g. PV) or GOAL/GK",
      "description": "Brief explanation"
    }},
    "game_state": "Attacking/Defending/Transition"
  }}
}}

CRITICAL: Return a JSON array with {len(batch)} objects, analyzing each frame in the grid from left to right, top to bottom.
"""
            
            # Create a grid image from the batch to provide temporal context
            # This avoids the cumulative history approach that caused Metal crashes
            grid_bytes = create_frame_grid(batch, cols=3)
            
            jobs[job_id]["status"] = f"Analyzing batch {b_idx+1}/{num_batches} (AI Thinking...)"
            
            # Analyze the grid as a single image
            response = processor.analyze_frame(grid_bytes, temporal_prompt)
            batch_results = extract_json(response)
            
            if isinstance(batch_results, list):
                pass # previous_batch_json = json.dumps(batch_results) # No longer needed
            elif isinstance(batch_results, dict):
                # VLM returned a single object instead of an array, wrap it
                batch_results = [batch_results]
                previous_batch_json = json.dumps(batch_results)
            else:
                batch_results = []

            # Save frames and clips
            for i, (ts, img_bytes) in enumerate(batch):
                idx = batch_start + i
                jobs[job_id]["status"] = f"Batch {b_idx+1}/{num_batches}: Saving frame {i+1}..."
                
                frame_name = f"frame_{idx}.jpg"
                clip_name = f"clip_{idx}.mp4"
                
                with open(job_dir / frame_name, "wb") as f:
                    f.write(img_bytes)
                
                extract_clip(req.video_path, ts, str(job_dir / clip_name))
                
                res = batch_results[i] if i < len(batch_results) else {}
                analysis_results.append({
                    "id": idx,
                    "timestamp": ts,
                    "frame_url": f"/data/{job_id}/{frame_name}",
                    "clip_url": f"/data/{job_id}/{clip_name}",
                    "inferred": res,
                    "verification": None
                })
            
            jobs[job_id]["results"] = analysis_results

        jobs[job_id]["status"] = "completed"
        with open(job_dir / "results.json", "w") as f:
            json.dump(jobs[job_id], f, indent=2)

    except Exception as e:
        jobs[job_id]["status"] = f"Error: {str(e)}"
        print(f"Error: {e}")

@app.post("/analyze")
async def start_analysis(req: AnalysisRequest, background_tasks: BackgroundTasks):
    job_id = f"job_{int(time.time())}"
    jobs[job_id] = {"status": "Starting...", "video": req.video_path, "results": []}
    background_tasks.add_task(run_analysis_task, job_id, req)
    return {"job_id": job_id}

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    if job_id not in jobs:
        disk_path = DATA_DIR / job_id / "results.json"
        if disk_path.exists():
            with open(disk_path, "r") as f: return json.load(f)
        raise HTTPException(status_code=404)
    return jobs[job_id]

@app.post("/jobs/{job_id}/verify")
def verify_result(job_id: str, frame_id: int, status: str):
    if job_id not in jobs: raise HTTPException(status_code=404)
    results_path = DATA_DIR / "verification_results.json"
    all_verifications = []
    if results_path.exists():
        with open(results_path, "r") as f: all_verifications = json.load(f)
    for res in jobs[job_id]["results"]:
        if res["id"] == frame_id:
            res["verification"] = status
            all_verifications = [v for v in all_verifications if not (v["job_id"] == job_id and v["frame_id"] == frame_id)]
            all_verifications.append({"job_id": job_id, "frame_id": frame_id, "timestamp": res["timestamp"], "inferred": res["inferred"], "verification": status, "at": time.strftime("%Y-%m-%d %H:%M:%S")})
            break
    with open(results_path, "w") as f: json.dump(all_verifications, f, indent=2)
    return {"status": "success"}

@app.get("/download-results")
def download_results():
    results_path = DATA_DIR / "verification_results.json"
    if not results_path.exists(): raise HTTPException(status_code=404)
    return FileResponse(results_path, media_type="application/json", filename="verification_results.json")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
