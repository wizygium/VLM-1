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
MODEL_NAME = "gemini-1.5-pro-002" # Caching robust model. User suggested 3-pro, but 1.5-pro is standard for caching. I'll make it configurable.

# --- Modular Prompts (The "Brain") ---
# We split the complexity of gemini_context_zones.md into distinct steps
ANALYSIS_TASKS = {
    # Step 1: Establish Ground Truth
    "1_setup": """
    TASK: SETUP & CONTEXT
    1. Identify the Attacking Team (Color) and Defending Team (Color).
    2. Determine the direction of play.
    3. Perform an "Initial Roll Call": List visible Attacking Roles (LW, LB, CB, RB, RW, PV) and their starting Zones.
    """,

    # Step 2: Defensive Structure (NEW)
    "2_defense_structure": """
    TASK: DEFENSIVE STRUCTURE & DEPTH
    Analyze the defensive structure details.
    1. **Defender Depth**: For each visible defender, be precise:
       - Are they standing **right on the 6m line**?
       - Have they **stepped out** (e.g. to 7-8m)? If so, did they leave a **gap behind them**?
       - Are they standing out near the **9m line**?
    2. **Formation**: Identify the overall shape (e.g. 6-0 flat, 5-1 aggressive).
    """,

    # Step 3: The Action Timeline
    "3_timeline": """
    TASK: EVENT TIMELINE
    Create a precise chronological log of all ball events and significant off-ball movements.
    - Timestamp every event.
    - Track the Ball: Who passes to whom? (e.g. "CB passes to RB").
    - Track Off-Ball Cuts: Does a player move into the line without the ball? (e.g. "CB cuts to Zone 3 becoming PV2").
    - Verfiy "Fake Passes": Do not log a pass if the player retains the ball.
    """,

    # Step 4: Synthesis
    "4_json": """
    TASK: JSON GENERATION
    Based on the Context, Defense, and Timeline you just established, generate the FINAL JSON output.
    
    Use this Schema:
    [
      { "video": "filename.mp4" },
      {
        "frame": {
          "time": "1.50 seconds",
          "visual_evidence": "...",
          "possession": { "team": "...", "player_role": "...", "zone": 8, "action": "..." },
          "event": { "type": "PASS", "from_role": "...", "to_role": "...", ... },
          "attackers": { "LW": 1, "LB": 6, "CB": 8, ... },
          "defensive_formation": {
            "formation_type": "6-0",
            "defenders": { "D1": 1, "D2": 2, ... }
          },
          "game_state": "Attacking"
        }
      }
    ]
    
    requirements:
    - DEFENSE: Populate 'defensive_formation' accurately based on the defense step.
    - ATTACKERS: Include 'PV2'.
    - Output ONLY the JSON block.
    """
}

class GeminiCacheAnalyzer:
    def __init__(self, api_key, model="gemini-1.5-pro-002", verbose=False):
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
        if self.verbose:
            print(f"  Creating High-Density Context Cache ({self.model_name})...")
            
        try:
            # Load the detailed Zone Definitions to bake into the cache system instruction
            # This makes the model "know" handball physics natively for this session
            zones_def_path = Path("gemini_context_zones.md")
            system_instruction = "You are a World-Class Handball Analyst."
            if zones_def_path.exists():
                with open(zones_def_path, 'r') as f:
                    system_instruction += "\n\n" + f.read()

            handball_cache = self.client.caches.create(
                model=self.model_name,
                config=types.CreateCachedContentConfig(
                    display_name=cache_name,
                    system_instruction=system_instruction,
                    contents=[video_file],
                    ttl=f"{CACHE_TTL_SECONDS}s"
                )
            )
        except Exception as e:
            print(f"❌ Cache Creation Error: {e}")
            return

        # 3. Run Modular Steps
        full_report_text = f"# Analysis Report: {video_path.name}\nDate: {datetime.now().isoformat()}\n\n"
        final_json = None
        
        chat_session = [] # Maintain history manually or via chat? 
        # Caching naturally supports stateless calls if we pass cache=name. 
        # But previous turns help next turns. 
        # We can use a chat session *linked* to the cache? 
        # Or just stateless calls where strict logical dependency isn't hard-coded in history.
        # Actually, for "Step 3: JSON" to know "Step 2: Timeline", we MUST include Step 2 output in Step 3 input
        # OR use a ChatSession bound to the cache. 
        # The Python SDK `client.chats.create(model=..., config=...)` supports `cached_content`.
        
        # Using Chat Session for Continuity
        chat = self.client.chats.create(
            model=self.model_name,
            config=types.GenerateContentConfig(
                cached_content=handball_cache.name,
                temperature=0.7 # Low temp for precision
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
        # We let it expire in 1h to allow inspection if needed
        print(f"  🕒 Cache TTL: 1h ({handball_cache.name})")

@click.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--output", "-o", default="results_cached", help="Output directory")
@click.option("--model", "-m", default="gemini-1.5-pro-002", help="Model to use")
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
