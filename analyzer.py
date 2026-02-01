#!/usr/bin/env python3
"""
Unified Handball Video Analyzer for Gemini.
Combines Modular Caching and Direct Physics Tracking.
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
CACHE_TTL_SECONDS = 3600
DEFAULT_MODEL = "gemini-3-pro-preview"
DEFAULT_FPS = 16.0

class HandballAnalyzer:
    def __init__(self, api_key, model=DEFAULT_MODEL, verbose=False):
        self.api_key = api_key
        self.model_name = model
        self.verbose = verbose
        self.client = genai.Client(api_key=api_key)

    def upload_video(self, video_path: Path):
        """Upload video to Gemini File API."""
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

    def get_prompt(self, prompt_name):
        """Load prompt from prompts/ directory."""
        path = Path(f"prompts/{prompt_name}")
        if not path.exists():
            # Fallback to local if not in prompts/
            path = Path(prompt_name)
        if path.exists():
            with open(path, 'r') as f:
                return f.read()
        return None

    def create_cache(self, video_file, system_instruction):
        """Create a Gemini Cache for the video."""
        cache_name = f"handball_cache_{int(time.time())}"
        part = types.Part.from_uri(file_uri=video_file.uri, mime_type=video_file.mime_type)
        part.video_metadata = types.VideoMetadata(fps=DEFAULT_FPS)
        content = types.Content(role="user", parts=[part])
        
        return self.client.caches.create(
            model=self.model_name,
            config=types.CreateCachedContentConfig(
                display_name=cache_name,
                system_instruction=system_instruction,
                contents=[content],
                ttl=f"{CACHE_TTL_SECONDS}s"
            )
        )

    def run_modular_analysis(self, video_path: Path, output_dir: Path):
        """Modular cached analysis (Best for complex reasoning)."""
        video_file = self.upload_video(video_path)
        system_instr = self.get_prompt("gemini_context_zones.md") or "You are a World-Class Handball Analyst."
        cache = self.create_cache(video_file, system_instr)
        
        # Modular Steps
        tasks = {
            "1_roster": "TASK: ROSTER LOCK. Identify attackers and defenders.",
            "2_ball": "TASK: BALL STATE TIMELINE. 16 FPS tracking. DO NOT SUMMARIZE.",
            "3_json": "TASK: JSON GENERATION. Produce final physics-compatible JSON."
        }
        
        chat = self.client.chats.create(
            model=self.model_name,
            config=types.GenerateContentConfig(
                cached_content=cache.name,
                temperature=0.2,
                media_resolution="MEDIA_RESOLUTION_HIGH"
            )
        )
        
        results = {}
        for key, prompt in tasks.items():
            if self.verbose: print(f"  👉 {key}...")
            resp = chat.send_message(prompt)
            results[key] = resp.text
            
        # Extract JSON from the last step
        try:
            text = results["3_json"].replace("```json", "").replace("```", "").strip()
            final_json = json.loads(text)
            self.save_output(video_path, output_dir, final_json)
        except Exception as e:
            print(f"❌ JSON Error: {e}")

    def run_direct_analysis(self, video_path: Path, output_dir: Path):
        """Direct single-step analysis (Fastest)."""
        video_file = self.upload_video(video_path)
        system_instr = self.get_prompt("physics_prompt.md") or "You are a physics observer."
        cache = self.create_cache(video_file, system_instr)
        
        prompt = "Output the FINAL JSON for the entire video at 16 FPS. Output JSON ONLY."
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                cached_content=cache.name,
                temperature=0.1,
                media_resolution="MEDIA_RESOLUTION_HIGH",
                response_mime_type="application/json"
            )
        )
        
        try:
            data = json.loads(response.text)
            self.save_output(video_path, output_dir, data)
        except Exception as e:
            print(f"❌ JSON Error: {e}")

    def save_output(self, video_path, output_dir, data):
        output_dir.mkdir(parents=True, exist_ok=True)
        json_path = output_dir / f"{video_path.stem}_analysis.json"
        wrapper = {
            "video_file": video_path.name,
            "model": self.model_name,
            "analysis": data
        }
        with open(json_path, 'w') as f:
            json.dump(wrapper, f, indent=2)
        print(f"  ✅ Saved: {json_path.name}")

@click.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--mode", type=click.Choice(["modular", "direct"]), default="modular")
@click.option("--model", default=DEFAULT_MODEL)
@click.option("--output", "-o", default="results")
@click.option("--api-key", envvar="GEMINI_API_KEY")
def main(input_path, mode, model, output, api_key):
    if not api_key:
        print("Set GEMINI_API_KEY.")
        return
    analyzer = HandballAnalyzer(api_key, model=model, verbose=True)
    input_path = Path(input_path)
    output_dir = Path(output)
    
    if input_path.is_file():
        if mode == "modular": analyzer.run_modular_analysis(input_path, output_dir)
        else: analyzer.run_direct_analysis(input_path, output_dir)
    else:
        for v in sorted(input_path.glob("*.mp4")):
            if mode == "modular": analyzer.run_modular_analysis(v, output_dir)
            else: analyzer.run_direct_analysis(v, output_dir)

if __name__ == "__main__":
    main()
