#!/usr/bin/env python3
"""Analyze handball match video using multi-frame sequence analysis."""

from __future__ import annotations

import base64
import io
import json
import math
import re
import click
import cv2
import numpy as np
import psutil
from tqdm import tqdm
from pathlib import Path

from vlm_1.processor import VideoProcessor

# Default prompt template
DEFAULT_PROMPT = """Grid of {num_frames} handball frames ({duration:.1f}s). Read left-to-right, top-to-bottom.

{match_info}
TEAMS: {team_context}

For EACH of the {num_frames} frames, analyze the player holding the ball:

1. What color is their jersey?
2. What team?
3. What shirt number is visible? (integer or null)
4. What action? (carry, pass, dribble, or shoot)
5. If shooting, did it go in? (success, miss, saved, or null if not shooting)

Return a JSON array with exactly {num_frames} objects.
Each object needs: frame, team_color, team, shirt_number, action, shot_outcome

JSON array only, no explanation."""


def extract_json(text: str) -> list | dict | None:
    """Extract JSON array or object from text, handling various formats."""
    # Try direct parse
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Find JSON array (starts with [)
    start = text.find('[')
    if start != -1:
        depth = 0
        for i, char in enumerate(text[start:], start):
            if char == '[':
                depth += 1
            elif char == ']':
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i+1])
                    except json.JSONDecodeError:
                        break

    # Find JSON object (starts with {)
    start = text.find('{')
    if start != -1:
        depth = 0
        for i, char in enumerate(text[start:], start):
            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i+1])
                    except json.JSONDecodeError:
                        break

    # Try markdown code blocks
    if "```" in text:
        for part in text.split("```"):
            cleaned = part.strip()
            if cleaned.startswith("json"):
                cleaned = cleaned[4:].strip()
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                continue

    return None


def create_frame_grid(frames: list[tuple[float, bytes]], cols: int = 3) -> bytes:
    """Create a labeled grid image from multiple frames."""
    if not frames:
        raise ValueError("No frames provided")

    # Decode all frames
    images = []
    for ts, img_bytes in frames:
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        images.append((ts, img))

    # Get dimensions from first image
    h, w = images[0][1].shape[:2]

    # Calculate grid dimensions
    rows = math.ceil(len(images) / cols)

    # Create grid canvas
    grid_h = rows * h
    grid_w = cols * w
    grid = np.zeros((grid_h, grid_w, 3), dtype=np.uint8)

    # Place images with labels
    for idx, (ts, img) in enumerate(images):
        row = idx // cols
        col = idx % cols
        y = row * h
        x = col * w

        # Place image
        grid[y:y+h, x:x+w] = img

        # Add frame label
        label = f"F{idx+1} ({ts:.1f}s)"
        cv2.putText(grid, label, (x + 10, y + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    # Encode to JPEG
    _, buffer = cv2.imencode(".jpg", grid, [cv2.IMWRITE_JPEG_QUALITY, 90])
    
    # Check size and resize if too large (to avoid MLX memory allocation errors)
    # Qwen2-VL uses dynamic resolution and can explode tokens if image is too big
    max_dim = 1536
    if grid_h > max_dim or grid_w > max_dim:
        scale = max_dim / max(grid_h, grid_w)
        new_h, new_w = int(grid_h * scale), int(grid_w * scale)
        grid_resized = cv2.resize(grid, (new_w, new_h), interpolation=cv2.INTER_AREA)
        _, buffer = cv2.imencode(".jpg", grid_resized, [cv2.IMWRITE_JPEG_QUALITY, 90])

    return buffer.tobytes()


def check_memory(required_gb: float = 8.0) -> bool:
    """Check if there is sufficient memory available."""
    available_gb = psutil.virtual_memory().available / (1024 ** 3)
    if available_gb < required_gb:
        return False
    return True


def load_context(context_path: str) -> dict:
    """Load team and match context from a JSON file."""
    try:
        with open(context_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        click.echo(f"Warning: Could not load context file: {e}", err=True)
        return {}


def analyze_sequence(frames: list[tuple[float, bytes]], processor: VideoProcessor, prompt_template: str, context: dict) -> list:
    """Create grid image and send to VLM for sequence analysis."""
    # Create grid image
    grid_bytes = create_frame_grid(frames, cols=3)

    # Calculate duration
    if len(frames) > 1:
        duration = frames[-1][0] - frames[0][0]
    else:
        duration = 0

    # Prepare team context string
    teams = context.get("teams", [])
    if teams:
        team_strs = [f"{t['color']} jersey = {t['name']}" for t in teams]
        team_context = ", ".join(team_strs)
    else:
        team_context = "WHITE jersey = ARGENTINA, BLACK jersey = JAPAN"

    match_info = context.get("match", "")
    if match_info:
        match_info = f"MATCH: {match_info}"

    # Build prompt
    full_prompt = prompt_template.format(
        num_frames=len(frames),
        duration=duration,
        match_info=match_info,
        team_context=team_context
    )

    response = processor.analyze_frame(grid_bytes, full_prompt)
    result = extract_json(response)
    return result if isinstance(result, list) else []


@click.command()
@click.argument("video_path", type=click.Path(exists=True))
@click.option("--output", "-o", default="stats.json", help="Output JSON file path.")
@click.option("--context", "-c", type=click.Path(exists=True), help="Path to context JSON file (teams, match info).")
@click.option("--start", "-s", default=0.0, type=float, help="Start time in seconds.")
@click.option("--fps", "-f", default=1.5, type=float, help="Frames per second to extract (default: 1.5).")
@click.option("--model", "-m", default="mlx-community/Qwen2.5-VL-7B-Instruct-4bit", help="MLX-VLM model path.")
@click.option("--batch-size", "-b", default=6, type=int, help="Number of frames per grid for analysis.")
def main(video_path: str, output: str, context: str, start: float, fps: float, model: str, batch_size: int):
    """Analyze handball video using multi-frame sequence analysis."""
    
    # 1. Memory Check
    click.echo("Checking system resources...")
    if not check_memory(8.0):
        available = psutil.virtual_memory().available / (1024 ** 3)
        if not click.confirm(f"Warning: Only {available:.1f}GB memory available. Model needs ~8GB. Continue?"):
            return

    # 2. Load context
    ctx_data = {}
    if context:
        ctx_data = load_context(context)
        click.echo(f"Loaded context from: {context}")

    # 3. Initialize processor (this loads the model)
    click.echo(f"Loading model: {model}...")
    processor = VideoProcessor(model_path=model)

    # 4. Extract frames
    click.echo(f"Extracting frames from {video_path}...")
    interval = 1.0 / fps
    
    # Simple extraction with tqdm
    cap = cv2.VideoCapture(video_path)
    total_frames_in_video = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    
    # Using a progress bar for extraction
    frames_all = processor.extract_frames(video_path, interval_seconds=interval)
    frames = [(ts, img) for ts, img in frames_all if ts >= start]
    
    if not frames:
        click.echo("No frames to analyze!")
        return

    click.echo(f"Extracted {len(frames)} frames. Starting analysis in batches of {batch_size}...")

    # 5. Analyze in batches
    all_results = []
    num_batches = math.ceil(len(frames) / batch_size)
    
    with tqdm(total=num_batches, desc="Analyzing batches") as pbar:
        for i in range(0, len(frames), batch_size):
            batch = frames[i:i + batch_size]
            batch_result = analyze_sequence(batch, processor, DEFAULT_PROMPT, ctx_data)
            if batch_result:
                all_results.extend(batch_result)
            pbar.update(1)

    # 6. Save results
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    output_data = {
        "video": video_path,
        "start_time": start,
        "end_time": frames[-1][0] if frames else start,
        "num_frames": len(frames),
        "fps": fps,
        "analysis": all_results,
        "context": ctx_data
    }

    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)

    click.echo(f"\nResults saved to: {output}\n")

    # 7. Print summary
    if all_results:
        click.echo("=== Analysis Summary ===")
        for event in all_results:
            frame = event.get('frame', '?')
            action = event.get('action', '?')
            team = event.get('team', event.get('team_color', '?'))
            num = event.get('shirt_number', '-')
            outcome = event.get('shot_outcome', '')
            outcome_str = f" -> {outcome}" if outcome else ""
            click.echo(f"  F{frame}: {team} #{num} - {action}{outcome_str}")

        # Summary stats
        actions = [e.get('action') for e in all_results if e.get('action')]
        click.echo("\nAction Totals:")
        for action in ['carry', 'pass', 'dribble', 'shoot']:
            count = actions.count(action)
            if count > 0:
                click.echo(f"  {action}: {count}")
    else:
        click.echo("No structured results found in VLM responses.")


if __name__ == "__main__":
    main()
