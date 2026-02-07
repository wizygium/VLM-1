#!/usr/bin/env python3
"""
Batch analyze handball videos using Gemini Caching API.
Outputs physics-based JSON with track IDs (no role inference).
"""

import time
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import click
from google import genai
from google.genai import types

# --- Configuration ---
CACHE_TTL_SECONDS = 3600  # 1 hour
MODEL_NAME = "gemini-3-pro-preview"
FPS = 16.0  # 16 FPS for physics tracking

# --- Load Physics Prompt ---
PHYSICS_PROMPT_PATH = Path(__file__).parent / "prompts" / "physics_prompt.md"

def load_physics_prompt() -> str:
    """Load the physics observer prompt from file."""
    if PHYSICS_PROMPT_PATH.exists():
        with open(PHYSICS_PROMPT_PATH, 'r') as f:
            return f.read()
    # Fallback inline prompt
    return """
You are a PHYSICS OBSERVER tracking handball players and ball position.

## COURT GEOMETRY (20m × 20m half-court)
- Origin: Bottom-left corner is (0,0)
- Goal: Centered at y=0, from x=8.5 to x=11.5

## ZONE SYSTEM (z0-z15)
Track zones based on distance from goal line.

## YOUR TASK
For EACH frame (every 0.0625s at 16fps):
1. Ball State: holder_track_id, zone, state (Holding/Dribbling/In-Air/Loose)
2. All Visible Players: track_id, zone, jersey_number (or null), team

## STRICT CONSTRAINTS
- NO EVENT NAMES: Never use Pass, Shot, Fake, Goal, Assist
- Use TRACK IDs (t1, t2, t3...) - same player = same ID across all frames
- ZONE FORMAT: Always "z" followed by number (z8, z3)

## OUTPUT FORMAT
Return ONLY valid JSON array. One object per frame.
```json
[
  {
    "timestamp": "0.0625",
    "ball": {"holder_track_id": "t1", "zone": "z8", "state": "Holding"},
    "players": [
      {"track_id": "t1", "zone": "z8", "jersey_number": "25", "team": "white"},
      {"track_id": "t2", "zone": "z9", "jersey_number": null, "team": "white"}
    ]
  }
]
```
"""


# --- Analysis Tasks (Physics-Based) ---
ANALYSIS_TASKS = {
    # Step 0: Configuration Verification
    "0_verify": """
    TASK: CONFIGURATION VERIFICATION
    1. Identify the video sampling rate (FPS) you are currently using.
    2. Confirm high spatial resolution (1120 tokens/frame).
    3. State if jersey numbers and ball textures are clearly visible.
    4. Count the approximate number of visible players.
    """,

    # Step 1: Track Assignment
    "1_track_assignment": """
    TASK: PLAYER TRACK ASSIGNMENT
    Objective: Assign persistent TRACK IDs to all visible players.
    
    1. For each visible player, assign a unique track_id: t1, t2, t3, etc.
    2. Record their team color if visible: "white", "blue", or "unknown"
    3. Record jersey number ONLY if clearly visible, otherwise null.
    
    Output format:
    ```
    PLAYER TRACKS at T=0:
    - t1: Team [white/blue/unknown], Jersey [number or null], Zone [z0-z15]
    - t2: Team [white/blue/unknown], Jersey [number or null], Zone [z0-z15]
    ... (continue for all visible players)
    ```
    
    CRITICAL: These track IDs MUST persist throughout the entire video.
    Same player = same track_id, even if jersey becomes unreadable.
    """,

    # Step 2: Ball State Timeline
    "2_ball_state": """
    TASK: BALL STATE TIMELINE (PHYSICS ONLY)
    Objective: Track the ball's holder and state across all frames.
    
    CONSTRAINTS:
    - Do NOT use words like "Pass", "Shot", "Feint", or "Assist"
    - Report ONLY physical states
    - Use strictly "z" prefixed zones (e.g., z8, z3)
    - Use TRACK IDs (t1, t2, t3...) NOT role names
    
    Format per timestamp (every ~0.0625s at 16fps, or every change of state):
    - [Time] Ball Holder: [track_id] | Zone: [z0-z15] | Status: [Holding/Dribbling/In-Air/Loose]
    
    Ball States:
    - Holding: Player gripping ball, ball stationary in hands
    - Dribbling: Ball bouncing, player in contact with ball
    - In-Air: Ball not touching any player (traveling)
    - Loose: Ball on ground, no player contact
    
    Example:
    - [0.00s] Ball Holder: t1 | Zone: z8 | Status: Holding
    - [0.50s] Ball Holder: t1 | Zone: z8 | Status: Holding
    - [1.00s] Ball Holder: null | Zone: z7 | Status: In-Air
    - [1.20s] Ball Holder: t3 | Zone: z3 | Status: Holding
    """,

    # Step 3: Player Position Timeline
    "3_positions": """
    TASK: PLAYER POSITION TIMELINE
    Objective: Track all visible player positions across key frames.
    
    For timestamps at ~0.5s intervals, list ALL visible players:
    - Use the same track_id assigned in Step 1
    - Record zone (z0-z15)
    - Note jersey number if visible (or null)
    
    Output format:
    ```
    FRAME at [Time]:
    - t1: Zone z8, Jersey 25, Team white
    - t2: Zone z9, Jersey null, Team white
    - t3: Zone z2, Jersey 11, Team blue
    ... (all visible players)
    ```
    
    CRITICAL: Track IDs must remain consistent across all frames!
    """,

    # Step 4: Sanity Check
    "4_sanity_check": """
    TASK: PHYSICS SANITY CHECK
    Objective: Review your observations for errors.
    
    Check 1: Teleportation. Did any player move > 3 zones in < 0.5 seconds? If yes, correct.
    Check 2: Track Consistency. Did you accidentally assign different track_ids to the same player?
    Check 3: Ball Continuity. Can the ball physically travel from one holder to another in the time given?
    
    Output: "Corrections made: [List corrections or 'None']"
    """,

    # Step 5: Final JSON Generation
    "5_json": """
    TASK: PHYSICS JSON GENERATION
    Objective: Generate the FINAL JSON with one frame object per timestamp.
    
    Output a JSON array of frame objects. Each frame contains:
    - timestamp: decimal seconds (e.g., "0.0625", "0.125", "0.1875")
    - ball: {"holder_track_id": "t1" or null, "zone": "z8", "state": "Holding"}
    - players: array of all visible players
    
    Schema per frame:
    {
      "timestamp": "0.0625",
      "ball": {
        "holder_track_id": "t1",
        "zone": "z8",
        "state": "Holding"
      },
      "players": [
        {"track_id": "t1", "zone": "z8", "jersey_number": "25", "team": "white"},
        {"track_id": "t2", "zone": "z9", "jersey_number": null, "team": "white"},
        {"track_id": "t3", "zone": "z2", "jersey_number": "11", "team": "blue"}
      ]
    }
    
    Requirements:
    - Output ONLY valid JSON array
    - Include frames at regular intervals (~0.5s recommended) 
    - Ball states: "Holding", "Dribbling", "In-Air", "Loose" ONLY
    - Zones: Always "z" + number (z0-z15)
    - track_id: MUST be consistent across frames (same player = same ID)
    - jersey_number: string or null (NEVER guess)
    """
}


class GeminiCacheAnalyzer:
    def __init__(self, api_key, model="gemini-3-pro-preview", verbose=False):
        self.api_key = api_key
        self.model_name = model
        self.verbose = verbose
        self.client = genai.Client(api_key=api_key)

    def upload_video(self, video_path: Path):
        """Upload to Gemini File API."""
        if self.verbose:
            print(f"  Uploading {video_path.name}...")
            
        video_file = self.client.files.upload(file=str(video_path))
        
        while video_file.state.name == 'PROCESSING':
            if self.verbose:
                print(".", end="", flush=True)
            time.sleep(2)
            video_file = self.client.files.get(name=video_file.name)
            
        if self.verbose:
            print(f" Ready: {video_file.name}")
            
        if video_file.state.name == 'FAILED':
            raise ValueError(f"Video processing failed: {video_file.state.name}")
            
        return video_file

    def analyze_video(self, video_path: Path, output_dir: Path):
        """Run the Physics Analysis Pipeline."""
        start_time = time.time()
        print(f"\n🎬 Processing: {video_path.name}")
        
        # 1. Upload
        try:
            video_file = self.upload_video(video_path)
        except Exception as e:
            print(f"❌ Upload Error: {e}")
            return

        # 2. Create Cache with Physics Prompt
        cache_name = f"handball_physics_{int(time.time())}"
        try:
            system_instruction = load_physics_prompt()
            
            if self.verbose:
                print(f"  Creating Physics Cache (FPS={FPS}, Resolution=HIGH, Model={self.model_name})...")
            
            part = types.Part.from_uri(
                file_uri=video_file.uri,
                mime_type=video_file.mime_type
            )
            part.video_metadata = types.VideoMetadata(fps=FPS)

            content = types.Content(
                role="user",
                parts=[part]
            )

            handball_cache = self.client.caches.create(
                model=self.model_name,
                config=types.CreateCachedContentConfig(
                    display_name=cache_name,
                    system_instruction=system_instruction,
                    contents=[content],
                    ttl=f"{CACHE_TTL_SECONDS}s"
                )
            )
        except Exception as e:
            print(f"❌ Cache Creation Error: {e}")
            return

        # 3. Run Analysis Steps
        config_verification = f"**Configuration Verification:**\n"
        config_verification += f"- **Target FPS:** {FPS}\n"
        config_verification += f"- **Spatial Resolution:** HIGH (1120 tokens/frame)\n"
        config_verification += f"- **Cache Name:** {handball_cache.name}\n"
        
        if hasattr(handball_cache, 'usage_metadata'):
            usage = handball_cache.usage_metadata
            config_verification += f"- **Total Tokens:** {usage.total_token_count}\n"
            
        if self.verbose:
            print(f"  Config Verified: {FPS} FPS, HIGH Resolution")

        full_report_text = f"# Physics Analysis Report: {video_path.name}\n"
        full_report_text += f"Date: {datetime.now().isoformat()}\n\n"
        full_report_text += config_verification + "\n---\n\n"
        
        final_json = None
        
        chat = self.client.chats.create(
            model=self.model_name,
            config=types.GenerateContentConfig(
                cached_content=handball_cache.name,
                temperature=0.3,  # Low temp for physics precision
                media_resolution="MEDIA_RESOLUTION_HIGH"
            )
        )

        for step_key, step_prompt in ANALYSIS_TASKS.items():
            if self.verbose:
                print(f"  👉 Running Step: {step_key} ...", end="", flush=True)
            
            step_config = None
            if "json" in step_key:
                step_config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1  # Very strict for JSON
                )
            
            response = chat.send_message(step_prompt, config=step_config)
            
            if self.verbose:
                print(" Done.")
            
            full_report_text += f"\n## [{step_key.upper()}]\n{response.text}\n"
            
            if "json" in step_key:
                try:
                    text = response.text.replace("```json", "").replace("```", "").strip()
                    final_json = json.loads(text)
                except Exception as e:
                    print(f"    ⚠️ JSON Parse Error: {e}")

        # 4. Save Outputs
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save Report
        report_path = output_dir / f"{video_path.stem}_report.md"
        with open(report_path, "w") as f:
            f.write(full_report_text)
        print(f"  📄 Report saved: {report_path.name}")
        
        # Save Physics JSON
        if final_json:
            json_path = output_dir / f"{video_path.stem}_physics.json"
            wrapper = {
                "video_file": video_path.name,
                "model": self.model_name,
                "fps": FPS,
                "frames": final_json if isinstance(final_json, list) else [final_json]
            }
            with open(json_path, "w") as f:
                json.dump(wrapper, f, indent=2)
            print(f"  ✅ Physics JSON saved: {json_path.name}")
        else:
            print("  ❌ No JSON produced.")

        elapsed = time.time() - start_time
        print(f"  ⏱️ Completed in {elapsed:.1f}s")


@click.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--output", "-o", default="results_physics", help="Output directory")
@click.option("--model", "-m", default="gemini-3-pro-preview", help="Model to use")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--api-key", envvar="GEMINI_API_KEY")
def main(input_path, output, model, verbose, api_key):
    if not api_key:
        print("Set GEMINI_API_KEY env var.")
        return
        
    analyzer = GeminiCacheAnalyzer(api_key, model=model, verbose=verbose)
    input_path = Path(input_path)
    output = Path(output)
    
    if input_path.is_file():
        analyzer.analyze_video(input_path, output)
    else:
        for v in sorted(input_path.glob("*.mp4")):
            analyzer.analyze_video(v, output)


if __name__ == "__main__":
    main()
