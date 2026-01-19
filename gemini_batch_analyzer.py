#!/usr/bin/env python3
"""Batch analyze handball videos using Gemini 3 Pro API with zone and defensive tracking."""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import click
from google import genai
from google.genai import types
from tqdm import tqdm

# Cost tracking (as of Jan 2026, approximate)
COST_PER_MIN = {
    "gemini-1.5-pro": 0.00525,
    "gemini-2.0-flash-exp": 0.00105,
}


class GeminiBatchAnalyzer:
    """Batch video analyzer using Gemini API (google-genai SDK)."""

    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-1.5-pro",
        output_dir: Path = Path("results"),
        verbose: bool = False,
    ):
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose
        
        # Initialize Clients
        # 1. Standard client for uploads/file operations (default timeouts)
        self.client = genai.Client(api_key=api_key)
        
        # 2. Generation client with long timeout for Gemini 3 thinking (20 mins in ms)
        self.gen_client = genai.Client(api_key=api_key, http_options={"timeout": 1200000})
        
        # Model config
        self.generate_config = types.GenerateContentConfig(
            temperature=1.0,
            response_mime_type="application/json",
            max_output_tokens=65536, # Increased for Gemini 1.5/2.0/3.0 models
            thinking_config=types.ThinkingConfig(include_thoughts=True),
            media_resolution=types.MediaResolution.MEDIA_RESOLUTION_MEDIUM,
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"
                ),
            ]
        )
        
        # Stats
        self.total_videos = 0
        self.successful = 0
        self.failed = 0
        self.total_duration = 0.0
        self.errors = []

    def load_context_prompt(self, context_path: Path) -> str:
        """Load the handball analysis context from markdown file."""
        if not context_path.exists():
            raise FileNotFoundError(f"Context file not found: {context_path}")
        
        with open(context_path, "r", encoding="utf-8") as f:
            return f.read()

    def upload_video(self, video_path: Path) -> Any:
        """Upload video to Gemini File API and wait for processing."""
        if self.verbose:
            click.echo(f"  Uploading {video_path.name}...")
        
        # Upload file (v1 SDK)
        # Note: 'file' argument based on checked usage
        video_file = self.client.files.upload(file=str(video_path))
        
        if self.verbose:
            click.echo(f"  File uploaded: {video_file.name} ({video_file.uri})")
        
        # Wait for processing (timeout after 5 minutes)
        start_wait = time.time()
        while video_file.state == "PROCESSING":
            elapsed = time.time() - start_wait
            if elapsed > 300:
                raise RuntimeError("Video processing timed out after 5 minutes")
            
            if self.verbose:
                click.echo(".", nl=False)
                sys.stdout.flush()
            
            time.sleep(2)
            video_file = self.client.files.get(name=video_file.name)
        
        if self.verbose:
            click.echo() # Newline after dots
            
        if video_file.state == "FAILED":
            raise RuntimeError(f"Video processing failed: {video_file.state}")
        
        return video_file

    def analyze_video(
        self,
        video_path: Path,
        context_prompt: str,
        match_context: dict | None = None,
    ) -> dict:
        """Analyze a single video and return structured JSON."""
        
        # Upload video
        video_file = self.upload_video(video_path)
        
        # Build prompt
        prompt_parts = [context_prompt]
        
        if match_context:
            teams = match_context.get("teams", [])
            if teams:
                team_info = ", ".join([f"{t['color']} = {t['name']}" for t in teams])
                prompt_parts.append(f"\n\nMATCH CONTEXT: {team_info}")
        
        prompt_parts.append(f"\n\nAnalyze this handball video scene and output the JSON array following the exact schema provided above.")
        
        full_prompt = "\n".join(prompt_parts)
        
        # Generate response (v1 SDK)
        if self.verbose:
            click.echo(f"  Generating analysis...")
        
        # v1 SDK generate_content signature: model, contents=[...], config=...
        # Add timeout (e.g. 10 minutes) if supported, otherwise rely on client defaults
        # Note: google-genai v1 usually supports 'config' but timeout might be on client or call.
        # We'll just print a message that it might take time.
        if not self.verbose:
            click.echo("  (This may take 1-2 minutes)...", nl=False)
            sys.stdout.flush()

        # Construct Part with VideoMetadata for custom FPS
        video_part = types.Part(
            file_data=types.FileData(
                file_uri=video_file.uri,
                mime_type=video_file.mime_type
            ),
            video_metadata=types.VideoMetadata(fps=5)
        )

        response = self.gen_client.models.generate_content(
            model=self.model_name,
            contents=[video_part, full_prompt],
            config=self.generate_config
        )
        
        if not self.verbose:
            click.echo(" Done.")
        
        # Extract all content from parts for the report
        full_text = ""
        json_text_accumulator = ""
        
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                # 1. Text Content
                if part.text:
                    full_text += f"\n[TEXT]:\n{part.text}\n"
                    json_text_accumulator += part.text
                
                # 2. Thought/Reasoning Content (Native Gemini 3 feature)
                # Check for 'thought' attribute or similar if available in this SDK version
                # If not explicitly 'text', we treat it as potentially thought or other modality
                # We'll try to capture it via repr() or specific attributes if known
                elif hasattr(part, 'thought') and part.thought:
                    full_text += f"\n[THOUGHT]:\n{part.thought}\n"
                elif hasattr(part, 'code_execution_result'):
                     full_text += f"\n[CODE EXECUTION]:\n{part.code_execution_result}\n"
                else:
                    # Fallback: dump the part representation to see what it is (e.g. thought_signature)
                    # We avoid dumping massive binary blobs if any, but for 'thought_signature' it's usually metadata
                    full_text += f"\n[NON-TEXT PART]: {type(part)}\n{part}\n"
        else:
            # Fallback if specific parts structure isn't matched
            full_text = response.text
            json_text_accumulator = response.text

        # 3. Usage Metadata (Token Counts)
        if response.usage_metadata:
            full_text += f"\n\n[METADATA]:\nToken Usage: {response.usage_metadata}\n"
            if self.verbose:
                # Calculate estimated cost for this single call if possible
                 pass # simplified

        # Robust JSON Extraction Strategy
        # 1. Search for all ```json ... ``` blocks
        import re
        json_candidates = []
        
        # Regex for fenced blocks (json or generic)
        fenced_blocks = re.findall(r"```(?:json)?\s*(\[.*?\])\s*```", json_text_accumulator, re.DOTALL)
        json_candidates.extend(fenced_blocks)
        
        # 2. Add the pure text from first [ to last ] as a candidate (fallback for no fences)
        try:
            start_idx = json_text_accumulator.find("[")
            end_idx = json_text_accumulator.rfind("]")
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_candidates.append(json_text_accumulator[start_idx:end_idx+1])
        except Exception:
            pass

        # 3. Try parsing candidates, prioritizing the LONGEST one first
        # This prevents picking up small snippets like [1, 2] from the text explanation
        json_candidates.sort(key=len, reverse=True)

        result = None
        error_msg = None
        
        for candidate in json_candidates:
            try:
                # Clean candidate
                candidate = candidate.strip()
                result = json.loads(candidate)
                # If success, break
                error_msg = None 
                break
            except json.JSONDecodeError as e:
                snippet = candidate[-100:] if len(candidate) > 100 else candidate
                error_msg = f"Failed to parse candidate: {e} at ...{snippet}"
                continue
        
        if result is not None:
             return {"json": result, "raw_text": full_text, "error": None}
        
        # If we get here, all failed
        if not error_msg:
            error_msg = "No JSON candidates found in response."
            
        return {"json": None, "raw_text": full_text, "error": error_msg}

    def validate_output(self, data: Any) -> tuple[bool, list[str]]:
        """Validate output JSON against expected schema."""
        errors = []
        
        if not isinstance(data, list):
            errors.append("Output must be a JSON array")
            return False, errors
        
        if len(data) < 2:
            errors.append("Array must have at least 2 elements (video object + frames)")
            return False, errors
        
        # Check video object
        if not isinstance(data[0], dict) or "video" not in data[0]:
            errors.append("First element must be video object with 'video' field")
        
        # Check frames
        for i, frame_obj in enumerate(data[1:], start=1):
            if not isinstance(frame_obj, dict) or "frame" not in frame_obj:
                errors.append(f"Element {i} must have 'frame' field")
                continue
            
            frame = frame_obj["frame"]
            
            # Check required fields
            required = ["time", "possession", "event", "defensive_formation", "game_state"]
            for field in required:
                if field not in frame:
                    errors.append(f"Frame {i}: Missing required field '{field}'")
            
            # Validate zones
            if "possession" in frame and "zone" in frame["possession"]:
                zone = frame["possession"]["zone"]
                if not (0 <= zone <= 13):
                    errors.append(f"Frame {i}: Invalid possession zone {zone} (must be 0-13)")
            
            if "event" in frame:
                event = frame["event"]
                for zone_field in ["from_zone", "to_zone", "origin_zone", "destination_zone"]:
                    if zone_field in event:
                        zone = event[zone_field]
                        if not (0 <= zone <= 13):
                            errors.append(f"Frame {i}: Invalid event {zone_field} {zone} (must be 0-13)")
            
            # Validate defensive formation
            if "defensive_formation" in frame:
                df = frame["defensive_formation"]
                if "defenders" in df:
                    for role, zone in df["defenders"].items():
                        if zone is not None and not (0 <= zone <= 13):
                            errors.append(f"Frame {i}: Invalid defender {role} zone {zone}")
            
            # Validate attackers (NEW)
            if "attackers" in frame:
                attackers = frame["attackers"]
                if not isinstance(attackers, dict):
                     errors.append(f"Frame {i}: 'attackers' must be a dictionary")
                else:
                    for role, zone in attackers.items():
                        if zone is not None and not (0 <= zone <= 13):
                            errors.append(f"Frame {i}: Invalid attacker {role} zone {zone}")
            else:
                pass # Optional for now, or make strict later
        
        return len(errors) == 0, errors

    def process_video(
        self,
        video_path: Path,
        context_prompt: str,
        match_context: dict | None = None,
    ) -> dict:
        """Process a single video and save results."""
        
        click.echo(f"\n📹 Processing: {video_path.name}")
        self.total_videos += 1
        
        start_time = time.time()
        
        try:
            # Analyze
            analysis_output = self.analyze_video(video_path, context_prompt, match_context)
            result = analysis_output.get("json")
            raw_text = analysis_output.get("raw_text", "")
            error_msg = analysis_output.get("error")
            
            # Save Raw Report (Reasoning/Thinking) - Save this BEFORE checking for errors
            report_file = self.output_dir / f"{video_path.stem}_report.md"
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(f"# Analysis Report: {video_path.name}\n")
                f.write(f"Model: {self.model_name}\n")
                f.write(f"Date: {datetime.now().isoformat()}\n\n")
                f.write(raw_text)
            
            if self.verbose:
                click.echo(f"  📄 Report saved: {report_file.name}")
            
            # Now check for fatal parsing errors
            if error_msg:
                # Raise the error now that the report is saved
                raise ValueError(error_msg)

            # Validate based on extracted JSON
            is_valid, validation_errors = self.validate_output(result)
            
            if not is_valid:
                click.echo(f"  ⚠️  Validation warnings: {len(validation_errors)} issues")
                if self.verbose:
                    for err in validation_errors[:5]:  # Show first 5
                        click.echo(f"     - {err}")
            
            # Save output JSON
            output_file = self.output_dir / f"{video_path.stem}_analysis.json"
            output_data = {
                "video_file": video_path.name,
                "processed_at": datetime.now().isoformat(),
                "model": self.model_name,
                "analysis": result,
                "validation": {
                    "passed": is_valid,
                    "errors": validation_errors,
                },
            }
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            elapsed = time.time() - start_time
            click.echo(f"  ✅ Completed in {elapsed:.1f}s → {output_file.name}")
            
            self.successful += 1
            return output_data
            
        except Exception as e:
            click.echo(f"  ❌ Error: {e}")
            self.failed += 1
            self.errors.append({
                "video": video_path.name,
                "error": str(e),
            })
            return None

    def process_batch(
        self,
        video_paths: list[Path],
        context_prompt: str,
        match_context: dict | None = None,
    ):
        """Process multiple videos."""
        
        click.echo(f"\n🎬 Batch processing {len(video_paths)} videos...")
        
        for video_path in video_paths:
            self.process_video(video_path, context_prompt, match_context)
        
        # Save summary
        self.save_summary()

    def save_summary(self):
        """Save batch processing summary."""
        
        summary = {
            "total_videos": self.total_videos,
            "successful": self.successful,
            "failed": self.failed,
            "model": self.model_name,
            "estimated_cost_usd": self.estimate_cost(),
            "errors": self.errors,
        }
        
        summary_file = self.output_dir / "batch_summary.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        click.echo(f"\n📊 Summary saved to: {summary_file}")
        click.echo(f"  Success: {self.successful}/{self.total_videos}")
        click.echo(f"  Failed: {self.failed}")
        
        cost = self.estimate_cost()
        if cost > 0:
            click.echo(f"  Estimated cost: ${cost:.4f} USD")

    def estimate_cost(self) -> float:
        """Estimate API cost based on videos processed."""
        # Rough estimate: assume average 6 seconds per video
        avg_duration_min = (self.successful * 6) / 60.0
        cost_rate = COST_PER_MIN.get(self.model_name, 0.005)
        return avg_duration_min * cost_rate


@click.command()
@click.argument("input_path", type=click.Path(exists=True), required=False)
@click.option("--output", "-o", default="results", help="Output directory for results.")
@click.option("--context", "-c", type=click.Path(exists=True), help="Match context JSON file.")
@click.option("--prompt", "-p", default="gemini_context_zones.md", help="Path to context prompt markdown file.")
@click.option("--model", "-m", default="gemini-1.5-pro", help="Gemini model to use.")
@click.option("--api-key", envvar="GEMINI_API_KEY", help="Gemini API key (or set GEMINI_API_KEY env var).")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output.")
@click.option("--list-models", is_flag=True, help="List available Gemini models.")
def main(
    input_path: str | None,
    output: str,
    context: str | None,
    prompt: str,
    model: str,
    api_key: str | None,
    verbose: bool,
    list_models: bool,
):
    """Batch analyze handball videos using Gemini 3 Pro API.
    
    INPUT_PATH can be a single video file or a directory of videos.
    """
    
    # Check API key
    if not api_key:
        click.echo("Error: GEMINI_API_KEY not set. Either:")
        click.echo("  1. Set environment variable: export GEMINI_API_KEY='your-key'")
        click.echo("  2. Use --api-key flag")
        click.echo("\nGet your API key at: https://aistudio.google.com/apikey")
        sys.exit(1)
        
    # Configure API - Initialize client
    client = genai.Client(api_key=api_key)

    # List models if requested
    if list_models:
        click.echo("Fetching available models...")
        try:
            models = client.models.list()
            click.echo("\nAvailable Gemini Models:")
            for m in models:
                # Check for generateContent support (field name might differ in v1 SDK, checking name convention)
                # v1 SDK models usually have supported_generation_methods or we list all.
                # Assuming all listed models are usable or filtering by common prefixes.
                click.echo(f"  - {m.name} ({m.display_name})")
            return
        except Exception as e:
            click.echo(f"Error listing models: {e}")
            sys.exit(1)
    
    # Needs input path if not listing models
    if not input_path:
        click.echo("Error: INPUT_PATH argument is required.")
        sys.exit(1)

    # Load context prompt
    prompt_path = Path(prompt)
    if not prompt_path.exists():
        click.echo(f"Error: Context prompt file not found: {prompt}")
        sys.exit(1)
    
    with open(prompt_path, "r", encoding="utf-8") as f:
        context_prompt = f.read()
    
    click.echo(f"📄 Loaded context prompt: {prompt_path}")
    
    # Load match context
    match_context = None
    if context:
        with open(context, "r", encoding="utf-8") as f:
            match_context = json.load(f)
        click.echo(f"📋 Loaded match context: {context}")
    
    # Get video files
    input_path = Path(input_path)
    if input_path.is_file():
        video_files = [input_path]
    elif input_path.is_dir():
        video_files = sorted(input_path.glob("*.mp4"))
        if not video_files:
            click.echo(f"No .mp4 files found in {input_path}")
            sys.exit(1)
    else:
        click.echo(f"Error: Invalid input path (must be file or directory): {input_path}")
        sys.exit(1)
    
    # Initialize analyzer
    analyzer = GeminiBatchAnalyzer(
        api_key=api_key,
        model_name=model,
        output_dir=Path(output),
        verbose=verbose,
    )
    
    # Process
    analyzer.process_batch(video_files, context_prompt, match_context)


if __name__ == "__main__":
    main()
