#!/usr/bin/env python3
"""
Physics-only handball video analyzer using Gemini-3-flash-preview.

Tracks observable physics only:
- Player positions (track IDs + zones)
- Ball state (holder, zone, state)
- NO event inference (PASS/SHOT done programmatically later)

Uses caching for efficiency with 16fps, HIGH resolution.
"""

import time
import json
import os
from pathlib import Path
from datetime import datetime
import click
from google import genai
from google.genai import types

# --- Configuration ---
CACHE_TTL_SECONDS = 3600  # 1 hour
MODEL_NAME = "gemini-3-flash-preview"
FPS = 16.0
TEMPERATURE = 0.2  # Very low for factual observation
MEDIA_RESOLUTION = "MEDIA_RESOLUTION_HIGH"  # 280 tokens/frame

# --- Analysis Task (Physics Only) ---
ANALYSIS_TASK = """
TASK: PHYSICS OBSERVATION

For EVERY frame at 16fps (0.0625s intervals), output:

1. **Ball State:**
   - holder_track_id: Track ID of player with ball (or null)
   - zone: Ball position (z0 or z{depth}_{lateral})
   - state: "Holding"|"Dribbling"|"In-Air"|"Loose"

2. **All Visible Players:**
   - track_id: Persistent ID (t1, t2, t3...) - MUST be consistent across frames
   - zone: Player position (z{depth}_{lateral})
   - jersey_number: Visible number or null
   - team: "white"|"blue"|"unknown" or null

CRITICAL RULES:
- Use SAME track_id for same player throughout video
- NEVER use event words: "Pass", "Shot", "Fake", "Goal"
- ONLY observable physics - no interpretation
- Zone format: z{depth}_{lateral} (e.g., z3_4, NOT z34)
- Output ONLY valid JSON array of frame objects

Return format:
```json
[
  {
    "timestamp": "0.0000",
    "ball": {
      "holder_track_id": "t1",
      "zone": "z3_4",
      "state": "Holding"
    },
    "players": [
      {"track_id": "t1", "zone": "z3_4", "jersey_number": "25", "team": "white"},
      {"track_id": "t2", "zone": "z3_5", "jersey_number": null, "team": "white"}
    ]
  },
  {
    "timestamp": "0.0625",
    "ball": {
      "holder_track_id": "t1",
      "zone": "z3_4",
      "state": "Holding"
    },
    "players": [
      {"track_id": "t1", "zone": "z3_4", "jersey_number": "25", "team": "white"},
      {"track_id": "t2", "zone": "z3_6", "jersey_number": "12", "team": "white"}
    ]
  }
]
```

Output JSON ONLY. No markdown, no other text.
"""


class GeminiPhysicsAnalyzer:
    """Physics-only handball video analyzer."""

    def __init__(self, api_key, model=MODEL_NAME, verbose=False):
        self.api_key = api_key
        self.model_name = model
        self.verbose = verbose
        self.client = genai.Client(api_key=api_key)

    def upload_video(self, video_path: Path):
        """Upload video to Gemini File API."""
        if self.verbose:
            print(f"  Uploading {video_path.name}...")

        video_file = self.client.files.upload(file=str(video_path))

        # Wait for State=ACTIVE
        while video_file.state.name == "PROCESSING":
            if self.verbose:
                print(".", end="", flush=True)
            time.sleep(2)
            video_file = self.client.files.get(name=video_file.name)

        if self.verbose:
            print(f" Ready: {video_file.name}")

        if video_file.state.name == "FAILED":
            raise ValueError(f"Video processing failed: {video_file.state.name}")

        return video_file

    def analyze_video(self, video_path: Path, output_dir: Path):
        """Run physics-only analysis pipeline."""
        start_time = time.time()
        print(f"\n🎬 Processing: {video_path.name}")

        # 1. Upload
        try:
            video_file = self.upload_video(video_path)
        except Exception as e:
            print(f"❌ Upload Error: {e}")
            return

        # 2. Create Physics-Only Cache
        cache_name = f"handball_physics_cache_{int(time.time())}"
        try:
            # Load physics prompt
            physics_prompt_path = Path("physics_prompt.md")
            system_instruction = "You are a PHYSICS OBSERVER for handball video analysis."
            if self.verbose:
                print(
                    f"  Creating cache (FPS={FPS}, Resolution=HIGH, "
                    f"Model={self.model_name})..."
                )
            if physics_prompt_path.exists():
                with open(physics_prompt_path, "r") as f:
                    system_instruction = f.read()

            # Create video part with metadata
            part = types.Part.from_uri(
                file_uri=video_file.uri, mime_type=video_file.mime_type
            )
            part.video_metadata = types.VideoMetadata(fps=FPS)

            content = types.Content(role="user", parts=[part])

            physics_cache = self.client.caches.create(
                model=self.model_name,
                config=types.CreateCachedContentConfig(
                    display_name=cache_name,
                    system_instruction=system_instruction,
                    contents=[content],
                    ttl=f"{CACHE_TTL_SECONDS}s",
                ),
            )
        except Exception as e:
            print(f"❌ Cache Creation Error: {e}")
            return

        # 3. Run Physics Analysis
        if self.verbose:
            print(f"  Running physics observation...")

        try:
            # Single generation call for all frames
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=ANALYSIS_TASK,
                config=types.GenerateContentConfig(
                    cached_content=physics_cache.name,
                    temperature=TEMPERATURE,
                    media_resolution=MEDIA_RESOLUTION,
                    response_mime_type="application/json",
                    max_output_tokens=65536,  # Allow large output for many frames
                ),
            )

            # Extract JSON
            try:
                text = response.text.replace("```json", "").replace("```", "").strip()
                physics_data = json.loads(text)
            except Exception as e:
                print(f"❌ JSON Parse Error: {e}")
                print(f"Response text: {response.text[:500]}...")
                return

        except Exception as e:
            print(f"❌ Generation Error: {e}")
            return

        # 4. Save Outputs
        output_dir.mkdir(parents=True, exist_ok=True)

        # Add metadata
        output = {
            "video": video_path.name,
            "metadata": {
                "fps": FPS,
                "resolution": "HIGH",
                "model": self.model_name,
                "timestamp": datetime.now().isoformat(),
                "total_frames": len(physics_data) if isinstance(physics_data, list) else 0,
            },
            "frames": physics_data if isinstance(physics_data, list) else [],
        }

        # Save physics JSON
        json_path = output_dir / f"{video_path.stem}_physics.json"
        with open(json_path, "w") as f:
            json.dump(output, f, indent=2)

        elapsed = time.time() - start_time
        print(f"  ✅ Physics JSON saved: {json_path.name}")
        print(f"  ⏱️  Completed in {elapsed:.1f}s")

        # Optional: Validate output
        try:
            from validate_physics_output import PhysicsValidator

            validator = PhysicsValidator()
            # Flatten structure for validation
            frames_only = output.get("frames", [])
            errors = validator.validate_all([output["metadata"]] + frames_only, fps=FPS)

            if errors:
                print(f"  ⚠️  Validation warnings ({len(errors)}):")
                for error in errors[:5]:  # Show first 5
                    print(f"    - {error}")
                if len(errors) > 5:
                    print(f"    ... and {len(errors) - 5} more")
            else:
                print(f"  ✅ Validation passed!")
        except ImportError:
            pass  # Validator not available


@click.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--output", "-o", default="results_physics", help="Output directory")
@click.option(
    "--model", "-m", default=MODEL_NAME, help="Model to use (default: gemini-3-flash-preview)"
)
@click.option("--api-key", envvar="GEMINI_API_KEY")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def main(input_path, output, model, api_key, verbose):
    """Analyze handball videos with physics-only tracking.

    INPUT_PATH: Video file (.mp4) or directory of videos

    Outputs physics JSON with track IDs, zones, and ball states at 16fps.
    """
    if not api_key:
        click.echo("Error: GEMINI_API_KEY not set. Either:")
        click.echo("  1. Set environment variable: export GEMINI_API_KEY='your-key'")
        click.echo("  2. Pass --api-key flag")
        return

    input_path = Path(input_path)
    output_dir = Path(output)

    analyzer = GeminiPhysicsAnalyzer(api_key=api_key, model=model, verbose=verbose)

    if input_path.is_file():
        # Single video
        analyzer.analyze_video(input_path, output_dir)
    elif input_path.is_dir():
        # Batch process
        videos = list(input_path.glob("*.mp4"))
        if not videos:
            click.echo(f"No .mp4 files found in {input_path}")
            return

        click.echo(f"Found {len(videos)} videos to process\n")
        for i, video_path in enumerate(videos, 1):
            click.echo(f"[{i}/{len(videos)}]")
            analyzer.analyze_video(video_path, output_dir)
            click.echo()
    else:
        click.echo(f"Error: {input_path} is neither file nor directory")


if __name__ == "__main__":
    main()
