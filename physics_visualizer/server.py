#!/usr/bin/env python3
"""
Physics Visualization Server

Streams videos from S3 and displays synchronized physics analysis
with interactive handball court visualization.
"""

import json
import os
from pathlib import Path
from typing import Optional
from datetime import timedelta

import boto3
from botocore.exceptions import ClientError
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


app = FastAPI(title="Handball Physics Visualizer")

# Add CORS middleware to allow browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent
RESULTS_DIR = Path(__file__).parent.parent / "results_physics"  # Look in parent directory

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


class AnalysisInfo(BaseModel):
    """Information about available physics analyses"""

    name: str
    physics_file: str
    events_file: Optional[str]
    s3_uri: str
    total_frames: int
    duration: float
    unique_players: int


# Initialize S3 client
try:
    s3_client = boto3.client("s3")
except Exception:
    s3_client = None


@app.get("/")
def read_root():
    """Serve the main visualization page"""
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/analyses")
def list_analyses():
    """List all available physics analyses"""
    print(f"DEBUG: Looking for analyses in {RESULTS_DIR}")
    print(f"DEBUG: RESULTS_DIR exists: {RESULTS_DIR.exists()}")
    
    if not RESULTS_DIR.exists():
        print("DEBUG: RESULTS_DIR does not exist!")
        return {"analyses": []}

    analyses = []

    # Find all physics JSON files
    physics_files = list(RESULTS_DIR.glob("*_physics.json"))
    print(f"DEBUG: Found {len(physics_files)} physics files")
    
    for physics_file in physics_files:
        try:
            print(f"DEBUG: Loading {physics_file.name}")
            with open(physics_file) as f:
                data = json.load(f)

            # Look for corresponding events file
            events_file = physics_file.parent / physics_file.name.replace(
                "_physics.json", "_events.json"
            )

            # Extract metadata
            metadata = data.get("metadata", {})
            frames = data.get("frames", [])

            # Calculate unique players
            unique_players = set()
            for frame in frames:
                for player in frame.get("players", []):
                    if player.get("track_id"):
                        unique_players.add(player["track_id"])

            analysis_dict = {
                "name": physics_file.stem.replace("_physics", ""),
                "physics_file": str(physics_file),
                "events_file": str(events_file) if events_file.exists() else None,
                "s3_uri": data.get("video", ""),
                "total_frames": metadata.get("total_frames", len(frames)),
                "duration": metadata.get("duration_seconds", len(frames) * 0.0625),
                "unique_players": len(unique_players),
            }
            analyses.append(analysis_dict)
            print(f"DEBUG: Added {analysis_dict['name']}")

        except Exception as e:
            print(f"Error loading {physics_file}: {e}")
            import traceback
            traceback.print_exc()
            continue

    print(f"DEBUG: Returning {len(analyses)} analyses")
    return {"analyses": sorted(analyses, key=lambda x: x["name"])}


@app.get("/api/physics/{analysis_name}")
def get_physics_data(analysis_name: str):
    """Get physics data for a specific analysis"""
    physics_file = RESULTS_DIR / f"{analysis_name}_physics.json"

    if not physics_file.exists():
        raise HTTPException(status_code=404, detail="Analysis not found")

    try:
        with open(physics_file) as f:
            data = json.load(f)

        return JSONResponse(content=data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/events/{analysis_name}")
def get_events_data(analysis_name: str):
    """Get events data for a specific analysis"""
    events_file = RESULTS_DIR / f"{analysis_name}_events.json"

    if not events_file.exists():
        raise HTTPException(status_code=404, detail="Events file not found")

    try:
        with open(events_file) as f:
            data = json.load(f)

        return JSONResponse(content=data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/video-url/{analysis_name}")
def get_video_url(analysis_name: str, expires_in: int = 3600):
    """Generate presigned S3 URL for video streaming"""
    if not s3_client:
        raise HTTPException(
            status_code=500, detail="AWS S3 client not configured"
        )

    # Get S3 URI from physics file
    physics_file = RESULTS_DIR / f"{analysis_name}_physics.json"

    if not physics_file.exists():
        raise HTTPException(status_code=404, detail="Analysis not found")

    try:
        with open(physics_file) as f:
            data = json.load(f)

        s3_uri = data.get("video", "")

        if not s3_uri.startswith("s3://"):
            raise HTTPException(status_code=400, detail="Invalid S3 URI")

        # Parse S3 URI
        parts = s3_uri[5:].split("/", 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else ""

        # Generate presigned URL
        try:
            presigned_url = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=expires_in,
            )

            return {"url": presigned_url, "expires_in": expires_in}

        except ClientError as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to generate presigned URL: {e}"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "s3_available": s3_client is not None,
        "results_dir": str(RESULTS_DIR),
        "results_dir_exists": RESULTS_DIR.exists(),
    }


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("Handball Physics Visualizer")
    print("=" * 60)
    print(f"Results directory: {RESULTS_DIR.absolute()}")
    print(f"S3 client available: {s3_client is not None}")
    print()
    print("Starting server at http://127.0.0.1:8001")
    print("=" * 60)

    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
