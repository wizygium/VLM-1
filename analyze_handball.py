#!/usr/bin/env python3
"""Analyze handball match video for player actions."""

from __future__ import annotations

import json
import re
import sys

import click

from vlm_1.processor import VideoProcessor

PROMPT = """Look at this handball match frame. Find the player holding the ball.

Return ONLY a JSON object with these fields:
- action: what they're doing ("shoot", "pass", or "dribble")
- team: their jersey color
- shirt_number: number on jersey (integer or null)
- confidence: 0.0 to 1.0

JSON only, no other text."""


def extract_json(text: str) -> dict | None:
    """Extract JSON object from text, handling various formats."""
    # Try direct parse first
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Find JSON object pattern anywhere in text
    match = re.search(r'\{[^{}]*"action"[^{}]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Try extracting from markdown code blocks
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            cleaned = part.strip()
            if cleaned.startswith("json"):
                cleaned = cleaned[4:].strip()
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                continue

    return None


@click.command()
@click.argument("video_path", type=click.Path(exists=True))
@click.option("--output", "-o", default="stats.json", help="Output JSON file path.")
@click.option("--start", "-s", default=0.0, type=float, help="Start time in seconds (skip frames before this).")
def main(video_path: str, output: str, start: float):
    """Analyze handball video for player actions (shoot/pass/dribble)."""
    processor = VideoProcessor(model="llama3.2-vision")

    click.echo(f"Analyzing handball video: {video_path}")
    click.echo(f"Extracting frames (1 per second, starting at {start}s)...")

    frames = processor.extract_frames(video_path, interval_seconds=1.0)
    frames = [(ts, img) for ts, img in frames if ts >= start]
    click.echo(f"Found {len(frames)} frames to analyze\n")

    results = []
    with click.progressbar(frames, label="Analyzing frames", show_pos=True) as bar:
        for timestamp, image_bytes in bar:
            response = processor.analyze_frame(image_bytes, PROMPT)

            # Extract JSON from response
            action_data = extract_json(response)
            if action_data is None:
                action_data = {"raw_response": response}

            results.append({
                "timestamp": timestamp,
                "analysis": action_data,
            })

    with open(output, "w") as f:
        json.dump(results, f, indent=2)

    click.echo(f"\nResults saved to: {output}")

    # Print summary
    actions = [r["analysis"].get("action", "unknown") for r in results]
    click.echo("\nSummary:")
    for action in ["shoot", "pass", "dribble", "none"]:
        count = actions.count(action)
        if count > 0:
            click.echo(f"  {action}: {count}")


if __name__ == "__main__":
    main()
