#!/usr/bin/env python3
"""
Physics-only handball analyzer with direct S3 streaming.

Downloads videos from S3 to temporary location, processes with Gemini,
then cleans up - avoiding disk space issues.
"""

import time
import json
import os
import tempfile
from pathlib import Path
from datetime import datetime
import click
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from google import genai
from google.genai import types

# --- Configuration (same as gemini_physics_analyzer.py) ---
CACHE_TTL_SECONDS = 3600
MODEL_NAME = "gemini-3-flash-preview"
FPS = 16.0
TEMPERATURE = 0.2
MEDIA_RESOLUTION = "MEDIA_RESOLUTION_HIGH"

# --- Analysis Task (10-Zone System: z0-z9) ---
ANALYSIS_TASK = """
TASK: PHYSICS OBSERVATION

For EVERY frame at 16fps (0.0625s intervals), output:

1. **Ball State:**
   - holder_track_id: Track ID of player with ball (or null)
   - zone: Ball position (z0 to z9)
   - state: "Holding"|"Dribbling"|"In-Air"|"Loose"

2. **All Visible Players:**
   - track_id: Persistent ID (t1, t2, t3...) - MUST be consistent across frames
   - zone: Player position (z0 to z9)
   - jersey_number: Visible number or null
   - team: "white"|"blue"|"unknown" or null

ZONE SYSTEM (10 zones):
- z0: Goal Area (inside 6m arc)
- z1: Band 1 Left (6m-9m, x<7.5m)
- z2: Band 1 Center (6m-9m, 7.5≤x≤12.5m)
- z3: Band 1 Right (6m-9m, x>12.5m)
- z4: Band 2 Left (9m-12m, x<7.5m)
- z5: Band 2 Center (9m-12m, 7.5≤x≤12.5m)
- z6: Band 2 Right (9m-12m, x>12.5m)
- z7: Band 3 Left (12m-20m, x<7.5m)
- z8: Band 3 Center (12m-20m, 7.5≤x≤12.5m)
- z9: Band 3 Right (12m-20m, x>12.5m)

CRITICAL RULES:
- Use SAME track_id for same player throughout video
- NEVER use event words: "Pass", "Shot", "Fake", "Goal"
- ONLY observable physics - no interpretation
- Zone format: z0, z1, z2... z9 (simple zone IDs)
- Output ONLY valid JSON array of frame objects

Return format:
```json
[
  {
    "timestamp": "0.0000",
    "ball": {
      "holder_track_id": "t1",
      "zone": "z5",
      "state": "Holding"
    },
    "players": [
      {"track_id": "t1", "zone": "z5", "jersey_number": "25", "team": "white"},
      {"track_id": "t2", "zone": "z6", "jersey_number": null, "team": "white"}
    ]
  }
]
```

Output JSON ONLY. No markdown, no other text.
"""


class S3PhysicsAnalyzer:
    """Physics analyzer with S3 streaming support."""

    def __init__(self, api_key, model=MODEL_NAME, aws_profile=None, verbose=False):
        self.api_key = api_key
        self.model_name = model
        self.verbose = verbose
        self.gemini_client = genai.Client(api_key=api_key)

        # Initialize S3 client
        session = boto3.Session(profile_name=aws_profile) if aws_profile else boto3.Session()
        self.s3_client = session.client("s3")

    def download_from_s3(self, s3_uri: str, temp_path: Path) -> bool:
        """Download video from S3 to temporary location.

        Args:
            s3_uri: S3 URI (s3://bucket/key)
            temp_path: Local temporary file path

        Returns:
            True if successful
        """
        try:
            # Parse S3 URI
            if not s3_uri.startswith("s3://"):
                raise ValueError(f"Invalid S3 URI: {s3_uri}")

            parts = s3_uri[5:].split("/", 1)
            bucket = parts[0]
            key = parts[1] if len(parts) > 1 else ""

            if self.verbose:
                print(f"  Downloading from S3: s3://{bucket}/{key}")

            # Download with progress
            self.s3_client.download_file(bucket, key, str(temp_path))

            if self.verbose:
                size_mb = temp_path.stat().st_size / (1024 * 1024)
                print(f"  Downloaded: {size_mb:.1f} MB")

            return True

        except (ClientError, NoCredentialsError) as e:
            print(f"❌ S3 Download Error: {e}")
            return False

    def upload_video_to_gemini(self, video_path: Path):
        """Upload video to Gemini File API."""
        if self.verbose:
            print(f"  Uploading to Gemini File API...")

        video_file = self.gemini_client.files.upload(file=str(video_path))

        # Wait for processing
        while video_file.state.name == "PROCESSING":
            if self.verbose:
                print(".", end="", flush=True)
            time.sleep(2)
            video_file = self.gemini_client.files.get(name=video_file.name)

        if self.verbose:
            print(f" Ready: {video_file.name}")

        if video_file.state.name == "FAILED":
            raise ValueError(f"Video processing failed: {video_file.state.name}")

        return video_file

    def analyze_video_from_s3(self, s3_uri: str, output_dir: Path, video_name: str = None):
        """Run physics analysis on S3 video.

        Args:
            s3_uri: S3 URI (s3://bucket/key.mp4)
            output_dir: Output directory for results
            video_name: Optional custom name (extracted from S3 key if not provided)
        """
        start_time = time.time()

        # Extract video name from S3 key if not provided
        if not video_name:
            video_name = Path(s3_uri.split("/")[-1]).stem

        print(f"\n🎬 Processing: {s3_uri}")

        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
            temp_path = Path(temp_file.name)

        try:
            # 1. Download from S3
            if not self.download_from_s3(s3_uri, temp_path):
                return

            # 2. Upload to Gemini
            try:
                video_file = self.upload_video_to_gemini(temp_path)
            except Exception as e:
                print(f"❌ Upload Error: {e}")
                return

            # 3. Create cache with physics prompt
            cache_name = f"handball_physics_cache_{int(time.time())}"
            try:
                physics_prompt_path = Path("physics_prompt.md")
                system_instruction = "You are a PHYSICS OBSERVER for handball video analysis."
                if physics_prompt_path.exists():
                    with open(physics_prompt_path, "r") as f:
                        system_instruction = f.read()

                if self.verbose:
                    print(
                        f"  Creating cache (FPS={FPS}, Resolution=HIGH, "
                        f"Model={self.model_name})..."
                    )

                part = types.Part.from_uri(
                    file_uri=video_file.uri, mime_type=video_file.mime_type
                )
                part.video_metadata = types.VideoMetadata(fps=FPS)
                content = types.Content(role="user", parts=[part])

                physics_cache = self.gemini_client.caches.create(
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

            # 4. Run physics analysis
            if self.verbose:
                print(f"  Running physics observation...")

            try:
                response = self.gemini_client.models.generate_content(
                    model=self.model_name,
                    contents=ANALYSIS_TASK,
                    config=types.GenerateContentConfig(
                        cached_content=physics_cache.name,
                        temperature=TEMPERATURE,
                        media_resolution=MEDIA_RESOLUTION,
                        response_mime_type="application/json",
                        max_output_tokens=65536,
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

            # 5. Save outputs
            output_dir.mkdir(parents=True, exist_ok=True)

            output = {
                "video": s3_uri,
                "metadata": {
                    "fps": FPS,
                    "resolution": "HIGH",
                    "model": self.model_name,
                    "timestamp": datetime.now().isoformat(),
                    "total_frames": len(physics_data) if isinstance(physics_data, list) else 0,
                },
                "frames": physics_data if isinstance(physics_data, list) else [],
            }

            json_path = output_dir / f"{video_name}_physics.json"
            with open(json_path, "w") as f:
                json.dump(output, f, indent=2)

            elapsed = time.time() - start_time
            print(f"  ✅ Physics JSON saved: {json_path.name}")
            print(f"  ⏱️  Completed in {elapsed:.1f}s")

            # Optional validation
            try:
                from validate_physics_output import PhysicsValidator

                validator = PhysicsValidator()
                errors = validator.validate_all(output.get("frames", []), fps=FPS)

                if errors:
                    print(f"  ⚠️  Validation warnings ({len(errors)}):")
                    for error in errors[:5]:
                        print(f"    - {error}")
                    if len(errors) > 5:
                        print(f"    ... and {len(errors) - 5} more")
                else:
                    print(f"  ✅ Validation passed!")
            except ImportError:
                pass

        finally:
            # 6. Clean up temporary file
            if temp_path.exists():
                temp_path.unlink()
                if self.verbose:
                    print(f"  🗑️  Cleaned up temporary file")


@click.command()
@click.argument("s3_uri")
@click.option("--output", "-o", default="results_physics", help="Output directory")
@click.option(
    "--model", "-m", default=MODEL_NAME, help="Model to use (default: gemini-3-flash-preview)"
)
@click.option("--api-key", envvar="GEMINI_API_KEY", help="Gemini API key")
@click.option("--aws-profile", help="AWS profile name (optional)")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--batch", is_flag=True, help="Process all videos in S3 prefix")
def main(s3_uri, output, model, api_key, aws_profile, verbose, batch):
    """Analyze handball videos from S3 with physics-only tracking.

    S3_URI: S3 URI (s3://bucket/video.mp4 or s3://bucket/prefix/ for batch)

    Examples:
      # Single video
      python gemini_s3_analyzer.py s3://my-bucket/handball/clip1.mp4

      # Batch process all videos in prefix
      python gemini_s3_analyzer.py s3://my-bucket/handball/ --batch
    """
    if not api_key:
        click.echo("Error: GEMINI_API_KEY not set. Either:")
        click.echo("  1. Set environment variable: export GEMINI_API_KEY='your-key'")
        click.echo("  2. Pass --api-key flag")
        return

    output_dir = Path(output)
    analyzer = S3PhysicsAnalyzer(
        api_key=api_key, model=model, aws_profile=aws_profile, verbose=verbose
    )

    if batch:
        # List all .mp4 files in S3 prefix
        if not s3_uri.endswith("/"):
            s3_uri += "/"

        parts = s3_uri[5:].split("/", 1)
        bucket = parts[0]
        prefix = parts[1] if len(parts) > 1 else ""

        try:
            session = (
                boto3.Session(profile_name=aws_profile)
                if aws_profile
                else boto3.Session()
            )
            s3_client = session.client("s3")

            response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)

            if "Contents" not in response:
                click.echo(f"No files found in {s3_uri}")
                return

            videos = [
                obj["Key"]
                for obj in response["Contents"]
                if obj["Key"].endswith(".mp4")
            ]

            if not videos:
                click.echo(f"No .mp4 files found in {s3_uri}")
                return

            click.echo(f"Found {len(videos)} videos to process\n")

            for i, key in enumerate(videos, 1):
                click.echo(f"[{i}/{len(videos)}]")
                video_uri = f"s3://{bucket}/{key}"
                video_name = Path(key).stem
                analyzer.analyze_video_from_s3(video_uri, output_dir, video_name)
                click.echo()

        except Exception as e:
            click.echo(f"Error listing S3 objects: {e}")
            return

    else:
        # Single video
        analyzer.analyze_video_from_s3(s3_uri, output_dir)


if __name__ == "__main__":
    main()
