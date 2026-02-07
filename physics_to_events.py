#!/usr/bin/env python3
"""
Stage 2: Physics to Events Transformer

Converts raw physics observations (*_physics.json) to enriched events (*_events.json)
by inferring player roles and deriving events programmatically.

Usage:
    python physics_to_events.py input_physics.json -o output_events.json
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

import click

from inference import (
    assign_attack_roles,
    assign_defense_roles,
    PlayerPosition,
    EventDetector,
)


def parse_physics_json(path: Path) -> Dict[str, Any]:
    """Load and validate physics JSON file."""
    with open(path, 'r') as f:
        data = json.load(f)
    
    if "frames" not in data:
        raise ValueError("Invalid physics JSON: missing 'frames' key")
    
    return data


def normalize_zone(zone: Any) -> int:
    """Convert zone to integer format."""
    if isinstance(zone, int):
        return zone
    if isinstance(zone, str):
        return int(zone.replace("z", ""))
    return 0


def build_roster(frames: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Build roster from first frame by assigning roles.
    """
    if not frames:
        return {"attack": [], "defense": []}
    
    first_frame = frames[0]
    players = first_frame.get("players", [])
    
    # Separate by team
    attackers = [
        PlayerPosition(
            track_id=p["track_id"],
            zone=normalize_zone(p.get("zone", 0)),
            jersey_number=p.get("jersey_number")
        )
        for p in players
        if p.get("team") in ["attack", "blue"]
    ]
    
    defenders = [
        PlayerPosition(
            track_id=p["track_id"],
            zone=normalize_zone(p.get("zone", 0)),
            jersey_number=p.get("jersey_number")
        )
        for p in players
        if p.get("team") in ["defense", "white"]
    ]
    
    # Assign roles
    attack_roles = assign_attack_roles(attackers)
    defense_roles = assign_defense_roles(defenders)
    
    roster = {
        "attack": [
            {
                "track_id": p.track_id,
                "role": attack_roles.get(p.track_id, "UNK"),
                "jersey_number": p.jersey_number
            }
            for p in attackers
        ],
        "defense": [
            {
                "track_id": p.track_id,
                "role": defense_roles.get(p.track_id, "UNK"),
                "jersey_number": p.jersey_number
            }
            for p in defenders
        ]
    }
    
    return roster


def get_all_roles(roster: Dict) -> Dict[str, str]:
    """Flatten roster to track_id -> role mapping."""
    roles = {}
    for team in roster.values():
        for player in team:
            roles[player["track_id"]] = player["role"]
    return roles


def enrich_frame_with_roles(frame: Dict, roles: Dict[str, str]) -> Dict:
    """Add role to each player in frame."""
    enriched = dict(frame)
    enriched["players"] = [
        {**p, "role": roles.get(p["track_id"], "UNK")}
        for p in frame.get("players", [])
    ]
    return enriched


def create_original_event(events: List[Dict], timestamp: float) -> Optional[Dict]:
    """Create backwards-compatible original_event field."""
    for event in events:
        if event.get("start_time", 0) <= timestamp <= event.get("end_time", float('inf')):
            return {
                "type": event.get("type", ""),
                "from_role": event.get("from_role") or event.get("role"),
                "from_zone": event.get("from_zone"),
                "to_role": event.get("to_role"),
                "to_zone": event.get("to_zone"),
                "description": f"{event.get('type', '')} event"
            }
    return None


def transform_physics_to_events(physics_data: Dict, source_path: Path) -> Dict:
    """Main transformation: physics -> events."""
    
    frames = physics_data.get("frames", [])
    metadata = physics_data.get("metadata", {})
    
    # Build roster from first frame
    roster = build_roster(frames)
    all_roles = get_all_roles(roster)
    
    # Collect attacker/defender IDs for turnover detection
    attacker_ids = {p["track_id"] for p in roster.get("attack", [])}
    defender_ids = {p["track_id"] for p in roster.get("defense", [])}
    
    # Detect events across all frames
    detector = EventDetector(all_roles, attacker_ids=attacker_ids, defender_ids=defender_ids)
    all_events = []
    
    for i in range(len(frames) - 1):
        is_last = (i == len(frames) - 2)
        frame_events = detector.detect_all_events(frames[i], frames[i + 1], is_last_frame=is_last)
        all_events.extend(frame_events)
    
    events_list = [e.to_dict() for e in all_events]
    
    # Build event index for active_event_ids
    def get_active_events(timestamp: float) -> List[int]:
        return [
            e["event_id"] for e in events_list
            if e["start_time"] <= timestamp <= e["end_time"]
        ]
    
    # Enrich frames
    enriched_frames = []
    for frame in frames:
        enriched = enrich_frame_with_roles(frame, all_roles)
        ts = frame.get("timestamp", 0)
        enriched["active_event_ids"] = get_active_events(ts)
        
        original = create_original_event(events_list, ts)
        if original:
            enriched["original_event"] = original
        
        enriched_frames.append(enriched)
    
    return {
        "metadata": {
            "video": metadata.get("video", physics_data.get("video", "")),
            "source_physics": str(source_path),
            "derived_at": datetime.now().isoformat(),
            "model": metadata.get("model", ""),
            "fps": metadata.get("fps"),
            "total_frames": len(frames),
            "duration_seconds": metadata.get("duration_seconds"),
        },
        "roster": roster,
        "events": events_list,
        "frames": enriched_frames,
    }


@click.command()
@click.argument("physics_json_path", type=click.Path(exists=True))
@click.option("-o", "--output", help="Output events JSON file")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def main(physics_json_path: str, output: str, verbose: bool):
    """Transform physics JSON to events JSON with role inference."""
    
    input_path = Path(physics_json_path)
    
    if not output:
        output = str(input_path).replace("_physics.json", "_events.json")
    output_path = Path(output)
    
    if verbose:
        click.echo(f"📖 Reading: {input_path}")
    
    physics_data = parse_physics_json(input_path)
    
    if verbose:
        click.echo(f"🔄 Transforming {len(physics_data.get('frames', []))} frames...")
    
    events_data = transform_physics_to_events(physics_data, input_path)
    
    with open(output_path, 'w') as f:
        json.dump(events_data, f, indent=2)
    
    # Summary
    n_attack = len(events_data['roster']['attack'])
    n_defense = len(events_data['roster']['defense'])
    n_events = len(events_data['events'])
    
    click.echo(f"\n✅ Output: {output_path}")
    click.echo(f"   Roster: {n_attack} attackers, {n_defense} defenders")
    click.echo(f"   Events: {n_events} detected")
    
    if verbose and events_data['events']:
        click.echo("\n📋 Events:")
        for e in events_data['events'][:10]:
            if e['type'] == 'PASS':
                click.echo(f"   PASS: {e.get('from_role')} → {e.get('to_role')} @ {e['start_time']:.1f}s")
            elif e['type'] == 'SHOT':
                click.echo(f"   SHOT: {e.get('from_role')} from z{e.get('from_zone')} → {e.get('outcome')}")
            elif e['type'] == 'MOVE':
                click.echo(f"   MOVE: {e.get('role')} z{e.get('from_zone')} → z{e.get('to_zone')}")


if __name__ == "__main__":
    main()
