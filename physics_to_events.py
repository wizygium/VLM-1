#!/usr/bin/env python3
"""
Derive PASS/SHOT events from physics-only JSON output.

Reads physics JSON (track IDs, zones, ball states) and infers events using
simple state machine rules. No VLM hallucination - pure programmatic logic.
"""

import json
from pathlib import Path
from typing import Optional
import click


def detect_events(physics_frames: list) -> list:
    """Derive PASS/SHOT events from physics facts using track IDs.

    Args:
        physics_frames: List of frame dictionaries from physics JSON

    Returns:
        List of event dictionaries with type, time, participants, zones
    """
    events = []

    for i in range(1, len(physics_frames)):
        prev = physics_frames[i - 1]
        curr = physics_frames[i]

        prev_ball = prev.get("ball", {})
        curr_ball = curr.get("ball", {})

        # PASS detection: holder track_id changed + ball was in-air
        prev_holder = prev_ball.get("holder_track_id")
        curr_holder = curr_ball.get("holder_track_id")

        if prev_holder != curr_holder and prev_ball.get("state") == "In-Air":
            # Get jersey numbers for enrichment (optional)
            from_jersey = _get_jersey(prev.get("players", []), prev_holder)
            to_jersey = _get_jersey(curr.get("players", []), curr_holder)

            events.append(
                {
                    "type": "PASS",
                    "time": prev.get("timestamp"),
                    "from_track_id": prev_holder,
                    "to_track_id": curr_holder,
                    "from_jersey": from_jersey,  # May be null
                    "to_jersey": to_jersey,  # May be null
                    "from_zone": prev_ball.get("zone"),
                    "to_zone": curr_ball.get("zone"),
                }
            )

        # SHOT detection: ball entered z0 (goal) + in-air
        if (
            prev_ball.get("zone") != "z0"
            and curr_ball.get("zone") == "z0"
            and curr_ball.get("state") == "In-Air"
        ):
            shooter_jersey = _get_jersey(prev.get("players", []), prev_holder)

            events.append(
                {
                    "type": "SHOT",
                    "time": curr.get("timestamp"),
                    "shooter_track_id": prev_holder,
                    "shooter_jersey": shooter_jersey,  # May be null
                    "from_zone": prev_ball.get("zone"),
                    "target_zone": "z0",
                }
            )

    return events


def _get_jersey(players: list, track_id: Optional[str]) -> Optional[str]:
    """Helper: Get jersey number for a track_id.

    Args:
        players: List of player dictionaries
        track_id: Track ID to look up

    Returns:
        Jersey number string or None
    """
    if not track_id:
        return None

    for p in players:
        if p.get("track_id") == track_id:
            return p.get("jersey_number")
    return None


def analyze_physics(data: dict) -> dict:
    """Analyze physics JSON and extract statistics.

    Args:
        data: Physics JSON with metadata and frames

    Returns:
        Statistics dictionary
    """
    frames = data.get("frames", [])
    if not frames:
        return {"error": "No frames found"}

    # Track unique players and jerseys
    track_ids = set()
    jerseys = set()
    ball_states = {"Holding": 0, "Dribbling": 0, "In-Air": 0, "Loose": 0}

    for frame in frames:
        # Ball states
        ball_state = frame.get("ball", {}).get("state")
        if ball_state in ball_states:
            ball_states[ball_state] += 1

        # Players
        for player in frame.get("players", []):
            tid = player.get("track_id")
            if tid:
                track_ids.add(tid)
            jersey = player.get("jersey_number")
            if jersey:
                jerseys.add(jersey)

    return {
        "total_frames": len(frames),
        "duration_seconds": len(frames) * 0.0625 if len(frames) > 0 else 0,
        "unique_track_ids": len(track_ids),
        "unique_jerseys": len(jerseys),
        "ball_states": ball_states,
    }


@click.command()
@click.argument("physics_json_path", type=click.Path(exists=True))
@click.option("-o", "--output", help="Output events JSON file")
@click.option("--stats", is_flag=True, help="Show statistics instead of events")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def main(physics_json_path, output, stats, verbose):
    """Derive events from physics JSON.

    PHYSICS_JSON_PATH: Path to physics JSON file from gemini_physics_analyzer.py

    Detects:
    - PASS events: Ball holder changed + ball in-air
    - SHOT events: Ball entered goal zone (z0) while in-air

    Events include track IDs and optional jersey numbers.
    """
    physics_path = Path(physics_json_path)

    # Load JSON
    with open(physics_path) as f:
        data = json.load(f)

    frames = data.get("frames", [])
    if not frames:
        click.echo("❌ No frames found in physics JSON")
        return

    if stats:
        # Show statistics
        stats_data = analyze_physics(data)
        click.echo("\n📊 Physics Statistics:")
        click.echo(f"  Frames: {stats_data.get('total_frames')}")
        click.echo(f"  Duration: {stats_data.get('duration_seconds'):.2f}s")
        click.echo(f"  Unique players (track IDs): {stats_data.get('unique_track_ids')}")
        click.echo(f"  Unique jerseys detected: {stats_data.get('unique_jerseys')}")
        click.echo("\n  Ball states:")
        for state, count in stats_data.get("ball_states", {}).items():
            pct = (count / stats_data.get("total_frames", 1)) * 100
            click.echo(f"    {state}: {count} ({pct:.1f}%)")
    else:
        # Detect events
        if verbose:
            click.echo(f"Analyzing {len(frames)} frames...")

        events = detect_events(frames)

        click.echo(f"\n🎯 Detected {len(events)} events:")
        click.echo(f"  PASS: {sum(1 for e in events if e['type'] == 'PASS')}")
        click.echo(f"  SHOT: {sum(1 for e in events if e['type'] == 'SHOT')}")

        if verbose and events:
            click.echo("\nEvent details:")
            for i, event in enumerate(events[:10], 1):  # Show first 10
                if event["type"] == "PASS":
                    from_j = event.get("from_jersey") or "?"
                    to_j = event.get("to_jersey") or "?"
                    click.echo(
                        f"  {i}. PASS @ {event['time']}s: "
                        f"#{from_j} → #{to_j} "
                        f"({event['from_zone']} → {event['to_zone']})"
                    )
                elif event["type"] == "SHOT":
                    shooter_j = event.get("shooter_jersey") or "?"
                    click.echo(
                        f"  {i}. SHOT @ {event['time']}s: "
                        f"#{shooter_j} from {event['from_zone']}"
                    )
            if len(events) > 10:
                click.echo(f"  ... and {len(events) - 10} more")

        # Save events JSON
        if output:
            output_path = Path(output)
            output_data = {
                "source_video": data.get("video"),
                "source_physics": physics_path.name,
                "metadata": data.get("metadata"),
                "events": events,
            }
            with open(output_path, "w") as f:
                json.dump(output_data, f, indent=2)
            click.echo(f"\n✅ Events saved to: {output_path}")


if __name__ == "__main__":
    main()
