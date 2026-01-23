#!/usr/bin/env python3
"""
Analyze handball videos using OpenRouter API (Nvidia Nemotron).
Extracts frames and sends them as a sequence of images to the VLM.
"""

import os
import cv2
import base64
import json
import time
import click
from pathlib import Path
from datetime import datetime
from openai import OpenAI
import math

# --- Configuration ---
MODEL_NAME = "nvidia/nemotron-nano-12b-v2-vl:free"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
FRAME_INTERVAL_SECONDS = 0.5  # Extract 1 frame every 0.5 seconds

# --- Modular Prompts (Adapted from gemini_cache_analyzer_v2.py) ---
ANALYSIS_TASKS = {
    # Step 0: Verification
    "0_verify": """
    TASK: CONFIGURATION VERIFICATION
    1. Confirm you can see the video frames.
    2. State if jersey numbers and ball textures are clearly visible.
    """,

    # Layer 1: Roster & Geometry Lock
    "1_roster_lock": """
    TASK: ROSTER & GEOMETRY LOCK
    Objective: Define the IMMUTABLE truths of the scene at T=0.
    1. **Attacking Roster**: List the 6 attackers (White/Japan). Assign a permanent ROLE (LW, LB, CB, RB, RW, PV) to each *visible* jersey number.
    2. **Defensive Roster**: List visible defenders (Blue/Argentina) and their starting Zones.
       - Use Standard Naming: DL1, DL2, DL3, DR3, DR2, DR1.
    3. **Geometry**: Identify the Goal Area Line (6m) and Free Throw Line (9m).
    """,

    # Layer 2: Ball State Timeline
    "2_ball_state": """
    TASK: BALL STATE TIMELINE (PHYSICS ONLY)
    Objective: Track the object (Ball) and its holder. specify timestamps.
    Constraint: Do NOT use words like "Pass", "Shot", "Feint", or "Assist".
    Constraint: Report ONLY physical states. Use strictly "z" prefixed zones (e.g. z10).
    
    Format per timestamp (every ~0.5s or change of state):
    - [Time] Ball Holder: [Role/Jersey] | Zone: [z0-z13] | Status: [Holding/Dribbling/In-Air/Loose]
    """,

    # Layer 3: Defensive Grid
    "3_defense_grid": """
    TASK: DEFENSIVE GRID ANALYSIS
    Objective: Analyze the defense INDEPENDENTLY of the ball.
    1. **Depth Check**: For DL3 and DR3, track their depth from the goal line (6m, 7m, 8m, 9m) at key timestamps.
    2. **Formation**: Identify if it is a flat 6-0 or if any defender steps out (5-1, usually ADV).
    """,

    # Layer 4: Tactical Synthesis
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

    # Layer 5: Sanity Check
    "5_sanity_check": """
    TASK: LOGIC & PHYSICS SANITY CHECK
    Objective: Review your own analysis for hallucinations.
    
    Check 1: Teleportation. Did any player move > 3 zones in < 0.5 seconds? If yes, correct the zone.
    Check 2: Role Consistency. Did "RB" suddenly become "CB"? Enforce Layer 1 Roster.
    Check 3: Ghost Events. Did you log a pass but the ball never left the player's hands? Remove it.
    
    Output: "Corrections made: [List corrections or 'None']"
    """,

    # Layer 6: Final JSON
    "6_json": """
    TASK: JSON GENERATION
    Objective: Generate the FINAL JSON based on the Corrected Synthesis.
    
    Use this Schema:
    [
      { "video": "filename.mp4" },
      {
        "frame": {
          "time": "1.50 seconds",
          "visual_evidence": "...",
          "possession": { "team": "...", "player_role": "...", "zone": "z8", "action": "..." },
          "event": { "type": "PASS", "from_role": "...", "to_role": "...", "outcome": "..." },
          "attackers": { "LW": "z1", "LB": "z6", ... },
          "defensive_formation": {
             "formation_type": "...",
             "defenders": { "DL1": "z1", "DL2": "z2", ... } 
          },
          "game_state": "Attacking"
        }
      }
    ]
    
    Requirements:
    - Output ONLY valid JSON.
    - Ensure logical continuity (from_zone of Event N+1 usually matches to_zone of Event N).
    - ALL ZONES MUST BE STRINGS STARTING WITH "z" (e.g., "z5", "z10").
    """
}

class OpenRouterAnalyzer:
    def __init__(self, api_key, model=MODEL_NAME, verbose=False):
        self.api_key = api_key
        self.model_name = model
        self.verbose = verbose
        self.client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=api_key
        )

    def extract_frames(self, video_path: Path):
        """Extract frames from video at specified interval."""
        if self.verbose:
            print(f"  Extracting frames from {video_path.name}...")
            
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
            
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps * FRAME_INTERVAL_SECONDS)
        
        frames = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_count % frame_interval == 0:
                # Encode frame to base64
                _, buffer = cv2.imencode('.jpg', frame)
                base64_frame = base64.b64encode(buffer).decode('utf-8')
                timestamp = frame_count / fps
                frames.append({
                    "timestamp": timestamp,
                    "base64": base64_frame
                })
                
            frame_count += 1
            
        cap.release()
        if self.verbose:
            print(f"  Extracted {len(frames)} frames.")
        return frames

    def analyze_video(self, video_path: Path, output_dir: Path):
        """Run the Analysis Pipeline."""
        start_time = time.time()
        print(f"\n🎬 Processing: {video_path.name}")
        
        # 1. Extract Frames
        try:
            frames = self.extract_frames(video_path)
            if not frames:
                print("❌ No frames extracted.")
                return
        except Exception as e:
            print(f"❌ Frame Extraction Error: {e}")
            return

        # 2. Prepare Context (System Prompt + Images)
        # Load zone definitions if available
        zones_def_path = Path("gemini_context_zones.md")
        system_instruction = "You are a World-Class Handball Analyst."
        if zones_def_path.exists():
            with open(zones_def_path, 'r') as f:
                system_instruction += "\n\n" + f.read()

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": []}
        ]

        # Add frames to the user message
        # Note: Some models might prefer separate messages or different formatting.
        # Standard OpenAI VLM format: content list with type='image_url'
        for f in frames:
            messages[-1]["content"].append({
                "type": "text",
                "text": f"Timestamp: {f['timestamp']:.2f}s"
            })
            messages[-1]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{f['base64']}",
                    "detail": "high" # Request high detail
                }
            })

        full_report_text = f"# Analysis Report: {video_path.name}\n"
        full_report_text += f"Date: {datetime.now().isoformat()}\n"
        full_report_text += f"Model: {self.model_name}\n"
        full_report_text += f"Frames: {len(frames)}\n---\n\n"
        
        final_json = None
        
        # 3. Run Modular Steps Sequentially
        # We accumulate history to maintain context
        
        for step_key, step_prompt in ANALYSIS_TASKS.items():
            if self.verbose:
                print(f"  👉 Running Step: {step_key} ...", end="", flush=True)

            # Append the current task prompt to the user message (or a new user message)
            # Since OpenAI API doesn't support appending to the *same* user message content once sent if we were doing stateless,
            # but here we are building a conversation.
            
            # For the FIRST step, the frames are already in the last message (user).
            # We append the specific task instruction to that SAME message if it's the first turn,
            # OR append a new user message for subsequent turns.
            
            if step_key == "0_verify":
                # First step: Add prompt to the existing message containing images
                messages[-1]["content"].append({
                    "type": "text",
                    "text": f"\n\n{step_prompt}"
                })
            else:
                # Subsequent steps: New user message
                messages.append({
                    "role": "user",
                    "content": step_prompt
                })

            try:
                # Force JSON format for the final step if supported, otherwise just normal
                response_format = None
                if "json" in step_key and "nemotron" not in self.model_name: # Nemotron might comply better without strict enforcement or different config
                     # Try to generic text first as OpenRouter implementation varies
                     pass
                
                completion = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.7 if "json" not in step_key else 0.1,
                )
                
                response_text = completion.choices[0].message.content
                
                # Append assistant response to history
                messages.append({
                    "role": "assistant",
                    "content": response_text
                })

                if self.verbose:
                    print(" Done.")
                
                full_report_text += f"\n## [{step_key.upper()}]\n{response_text}\n"

                if "json" in step_key:
                    try:
                        # Attempt to parse JSON
                        # Find the first [ and last ]
                        start = response_text.find('[')
                        end = response_text.rfind(']') + 1
                        if start != -1 and end != -1:
                            json_str = response_text[start:end]
                            final_json = json.loads(json_str)
                    except Exception as e:
                        print(f"    ⚠️ JSON Parse Error: {e}")

            except Exception as e:
                print(f"  ❌ API Error: {e}")
                # Don't break completely, try to continue or just stop? 
                # If a step fails, context might be broken.
                break

        # 4. Save Outputs
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / f"{video_path.stem}_report_openrouter.md"
        with open(report_path, "w") as f:
            f.write(full_report_text)
            
        print(f"  📄 Report saved: {report_path.name}")
        
        if final_json:
            json_path = output_dir / f"{video_path.stem}_analysis_openrouter.json"
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

@click.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--output", "-o", default="results_openrouter", help="Output directory")
@click.option("--model", "-m", default=MODEL_NAME, help="Model to use")
@click.option("--api-key", envvar="OPENROUTER_API_KEY")
@click.option("--interval", default=0.5, help="Frame extraction interval in seconds")
def main(input_path, output, model, api_key, interval):
    global FRAME_INTERVAL_SECONDS
    FRAME_INTERVAL_SECONDS = interval
    
    if not api_key:
        print("Set OPENROUTER_API_KEY env var.")
        return
        
    analyzer = OpenRouterAnalyzer(api_key, model=model, verbose=True)
    input_path = Path(input_path)
    output = Path(output)
    
    if input_path.is_file():
        analyzer.analyze_video(input_path, output)
    else:
        for v in sorted(input_path.glob("*.mp4")):
            analyzer.analyze_video(v, output)

if __name__ == "__main__":
    main()
