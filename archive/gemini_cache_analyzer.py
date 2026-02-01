#!/usr/bin/env python3
"""
Batch analyze handball videos using Gemini Caching API and Modular Prompts.
Fixes timeouts by splitting analysis into smaller, cached steps.
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
CACHE_TTL_SECONDS = 3600 # 1 hour
MODEL_NAME = "gemini-1.5-pro-001" # Caching robust model.

# --- Modular Prompts (The "Brain") ---
# We split the complexity of gemini_context_zones.md into distinct steps
# --- Modular Prompts (The "Brain") ---
ANALYSIS_TASKS = {
    # Step 0: Verification (Technical)
    "0_verify": """
    TASK: CONFIGURATION VERIFICATION
    1. Identify the video sampling rate (FPS) you are currently using.
    2. Confirm high spatial resolution (1120 tokens/frame).
    3. State if jersey numbers and ball textures are clearly visible.
    """,

    # Layer 1: Roster & Geometry Lock (Static Truth)
    "1_roster_lock": """
    TASK: ROSTER & GEOMETRY LOCK
    Objective: Define the IMMUTABLE truths of the scene at T=0.
    1. **Attacking Roster**: List the 6 attackers (White/Japan). Assign a permanent ROLE (LW, LB, CB, RB, RW, PV) to each *visible* jersey number.
    2. **Defensive Roster**: List visible defenders (Blue/Argentina) and their starting Zones.
       - Use Standard Naming: DL1, DL2, DL3, DR3, DR2, DR1.
    3. **Geometry**: Identify the Goal Area Line (6m) and Free Throw Line (9m).
    """,

    # Layer 2: Ball State Timeline (Physics Only)
    "2_ball_state": """
    TASK: BALL STATE TIMELINE (PHYSICS ONLY)
    Objective: Track the object (Ball) and its holder with HIGH TEMPORAL RESOLUTION.
    Constraint: Report at 16 FPS (approx every 0.0625s) for the ENTIRE duration.
    Constraint: Do NOT summarize. Every frame must have an entry if movement occurs.
    Constraint: Do NOT use words like "Pass", "Shot", "Feint", or "Assist".
    Constraint: Report ONLY physical states. Use strictly "z" prefixed zones (e.g. z10).
    Constraint: Do NOT infer a pass if the ball is bounced/dribbled. A bounce returns possession to the SAME player.
    Constraint: Only log a new 'Ball Holder' if you see the ball physically secured by a *different* player.
    
    Format per timestamp (Frame-by-Frame, approx every 0.06s / 16 FPS):
    - [Time] Ball Holder: [Role/Jersey] | Zone: [z0-z13] | Status: [Holding/Dribbling/In-Air (Pass)/In-Air (Bounce)/Loose]
    
    Example:
    - [0.00s] Ball Holder: RB (#25) | Zone: z10 | Status: Holding
    - [0.06s] Ball Holder: RB (#25) | Zone: z10 | Status: Holding
    - [0.12s] Ball Holder: RB (#25) | Zone: z9 | Status: Dribbling (In-Air Bounce)
    - [1.2s] Ball Holder: None (In-Air) | Zone: z8 | Status: In-Air (Pass to CB)
    - [1.3s] Ball Holder: CB (#5) | Zone: z8 | Status: Holding
    """,

    # Layer 3: Defensive Grid (Independent)
    "3_defense_grid": """
    TASK: DEFENSIVE GRID ANALYSIS
    Objective: Analyze the defense INDEPENDENTLY of the ball.
    1. **Depth Check**: For DL3 and DR3, track their depth from the goal line (6m, 7m, 8m, 9m) at key timestamps.
    2. **Formation**: Identify if it is a flat 6-0 or if any defender steps out (5-1, usually ADV).
    """,

    # Layer 4: Tactical Synthesis (The "Why")
    "4_tactical_synthesis": """
    TASK: TACTICAL SYNTHESIS
    Objective: Combine Layer 1 (Roster) and Layer 2 (Ball State) to infer distinct Events.
    
    Instructions:
    - Look at Layer 2. If 'Ball Holder' changed from RB to CB, and 'Status' went 'In-Air', classify this as a PASS.
    - If 'Ball Holder' led to 'Goal', classify as SHOT.
    
    Output a Narrative Timeline:
    - [Time] [Event Type] [Description]
    - Explicitly confirm: "Visual evidence supports this is a PASS, not a fake."
    """,

    # Layer 5: Sanity Check (Reflection)
    "5_sanity_check": """
    TASK: LOGIC & PHYSICS SANITY CHECK
    Objective: Review your own analysis for hallucinations.
    
    Check 1: Teleportation. Did any player move > 3 zones in < 0.5 seconds? If yes, correct the zone.
    Check 2: Role Consistency. Did "RB" suddenly become "CB"? Enforce Layer 1 Roster.
    Check 3: Ghost Events/Dribble Check. Review the Ball State timeline. If Player A 'passes' to Player B, but Player B is just Player A after a cut/dribble (or if the 'pass' was actually a bounce), MERGE these into a single possession.
    Check 4: Velocity Check. Does a 0.5s exchange between LB and CB make physics sense? If not, it's likely a single player moving.
    
    Output: "Corrections made: [List corrections or 'None']"
    """,

    # Layer 6: Final JSON
    "6_json": """
    TASK: JSON GENERATION
    Objective: Generate the FINAL JSON with HIGH DENSITY.
    
    Requirements:
    - Output ONLY valid JSON.
    - DO NOT SUMMARIZE. Provide a 'frame' object for at least 30-50 timestamps across the duration to ensure smooth visualization.
    - Ensure logical continuity (from_zone of Event N+1 usually matches to_zone of Event N).
    - ALL ZONES MUST BE STRINGS STARTING WITH "z" (e.g., "z5", "z10").
    """
}

class GeminiCacheAnalyzer:
    def __init__(self, api_key, model="gemini-3-pro", verbose=False):
        self.api_key = api_key
        self.model_name = model
        self.verbose = verbose
        # Client for standard ops
        self.client = genai.Client(api_key=api_key)

    def upload_video(self, video_path: Path):
        """Upload to Gemini File API."""
        if self.verbose:
            print(f"  Uploading {video_path.name}...")
            
        video_file = self.client.files.upload(file=str(video_path))
        
        # Wait for State=ACTIVE
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
        """Run the Cached Modular Analysis Pipeline."""
        start_time = time.time()
        print(f"\n🎬 Processing: {video_path.name}")
        
        # 1. Upload
        try:
            video_file = self.upload_video(video_path)
        except Exception as e:
            print(f"❌ Upload Error: {e}")
            return

        # 2. Create High-Density Cache
        cache_name = f"handball_cache_{int(time.time())}"
        try:
            # Load the detailed Zone Definitions to bake into the cache system instruction
            # This makes the model "know" handball physics natively for this session
            zones_def_path = Path("gemini_context_zones.md")
            system_instruction = "You are a World-Class Handball Analyst."
            if self.verbose:
                 print(f"  Creating Ultra-Density Cache (FPS=10, Resolution=HIGH, Model={self.model_name})...")
            if zones_def_path.exists():
                with open(zones_def_path, 'r') as f:
                    system_instruction += "\n\n" + f.read()
            # Construct Content with Part.from_uri as requested
            part = types.Part.from_uri(
                file_uri=video_file.uri,
                mime_type=video_file.mime_type
            )
            part.video_metadata = types.VideoMetadata(fps=16.0) 

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

        # 3. Run Modular Steps
        config_verification = f"**Configuration Verification:**\n"
        config_verification += f"- **Target FPS:** 16.0\n"
        config_verification += f"- **Spatial Resolution:** HIGH (1120 tokens/frame)\n"
        config_verification += f"- **Cache Name:** {handball_cache.name}\n"
        
        # Try to extract usage metadata
        if hasattr(handball_cache, 'usage_metadata'):
            usage = handball_cache.usage_metadata
            config_verification += f"- **Total Tokens:** {usage.total_token_count}\n"
            
        if self.verbose:
            print(f"  Config Verified: 10 FPS, HIGH Resolution")

        full_report_text = f"# Analysis Report: {video_path.name}\n"
        full_report_text += f"Date: {datetime.now().isoformat()}\n\n"
        full_report_text += config_verification + "\n---\n\n"
        
        final_json = None
        
        # Using Chat Session for Continuity with High Resolution
        chat = self.client.chats.create(
            model=self.model_name,
            config=types.GenerateContentConfig(
                cached_content=handball_cache.name,
                temperature=0.7, # Low temp for precision
                media_resolution="MEDIA_RESOLUTION_HIGH" # High Spatial Density (280 tokens/frame)
            )
        )

        for step_key, step_prompt in ANALYSIS_TASKS.items():
            if self.verbose:
                print(f"  👉 Running Step: {step_key} ...", end="", flush=True)
            
            # Refine Step Config -> JSON
            step_config = None
            if "json" in step_key:
                 step_config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1 # Very strict for JSON
                 )
            
            response = chat.send_message(step_prompt, config=step_config)
            
            if self.verbose:
                print(" Done.")
            
            full_report_text += f"\n## [{step_key.upper()}]\n{response.text}\n"
            
            if "json" in step_key:
                try:
                    # Clean markdown if needed
                    text = response.text.replace("```json", "").replace("```", "").strip()
                    final_json = json.loads(text)
                except Exception as e:
                    print(f"    ⚠️ JSON Parse Error: {e}")

        # 4. Save Outputs
        # Save Text Report
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / f"{video_path.stem}_report.md"
        with open(report_path, "w") as f:
            f.write(full_report_text)
            
        print(f"  📄 Report saved: {report_path.name}")
        
        # Save JSON
        if final_json:
            json_path = output_dir / f"{video_path.stem}_analysis.json"
            wrapper = {
                "video_file": video_path.name,
                "model": self.model_name,
                "analysis": final_json
            }
            with open(json_path, "w") as f:
                json.dump(wrapper, f, indent=2)
            print(f"  ✅ JSON saved: {json_path.name}")
        else:
            print("  ❌ No JSON produced.")

        # Cleanup Cache (Optional, but polite)
        # client.caches.delete(name=handball_cache.name)
        # We let it expire in 1h to# --- Configuration ---
CACHE_TTL_SECONDS = 3600 # 1 hour
MODEL_NAME = "gemini-3-pro-preview" # Caching robust model.

# ... (start of main)

@click.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--output", "-o", default="results_cached", help="Output directory")
@click.option("--model", "-m", default="gemini-3-pro-preview", help="Model to use")
@click.option("--api-key", envvar="GEMINI_API_KEY")
def main(input_path, output, model, api_key):
    if not api_key:
        print("Set GEMINI_API_KEY env var.")
        return
        
    analyzer = GeminiCacheAnalyzer(api_key, model=model, verbose=True)
    input_path = Path(input_path)
    output = Path(output)
    
    if input_path.is_file():
        analyzer.analyze_video(input_path, output)
    else:
        for v in sorted(input_path.glob("*.mp4")):
            analyzer.analyze_video(v, output)

if __name__ == "__main__":
    main()
