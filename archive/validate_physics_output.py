#!/usr/bin/env python3
"""
Physics-only handball analysis validator.

Validates:
- Schema compliance (track IDs, zones, ball states)
- Temporal consistency (timestamps increment correctly)
- Zone adjacency (players only move to adjacent zones)
- Track ID persistence (same ID across frames)
"""

import json
from pathlib import Path
from typing import Optional


class ZoneGraph:
    """Handball court zone adjacency for physics validation."""

    @staticmethod
    def parse_zone(zone: str) -> Optional[tuple[int, int]]:
        """Parse zone string to (depth, lateral) tuple.

        Args:
            zone: Zone string (e.g., "z0", "z3_4")

        Returns:
            (depth, lateral) tuple or None if invalid
        """
        if zone == "z0":
            return (0, 0)  # Goal
        try:
            parts = zone.replace("z", "").split("_")
            if len(parts) == 2:
                return (int(parts[0]), int(parts[1]))
        except (ValueError, IndexError):
            pass
        return None

    @staticmethod
    def get_adjacent_zones(zone: str) -> set[str]:
        """Get all zones adjacent to given zone.

        Args:
            zone: Zone string

        Returns:
            Set of adjacent zone strings (includes zone itself)
        """
        parsed = ZoneGraph.parse_zone(zone)
        if not parsed:
            return set()

        depth, lateral = parsed
        adjacent = set()

        # Special case: goal zone
        if depth == 0:
            # Can move to any z1_* zone (1m from goal)
            return {f"z1_{w}" for w in range(1, 9)} | {"z0"}

        # Adjacent in depth (±1)
        for d in [depth - 1, depth + 1]:
            if 0 <= d <= 6:
                if d == 0:
                    adjacent.add("z0")
                else:
                    adjacent.add(f"z{d}_{lateral}")

        # Adjacent laterally (±1)
        for w in [lateral - 1, lateral + 1]:
            if 1 <= w <= 8:
                adjacent.add(f"z{depth}_{w}")

        # Diagonal adjacency (±1 depth AND ±1 lateral)
        for d in [depth - 1, depth + 1]:
            for w in [lateral - 1, lateral + 1]:
                if (1 <= d <= 6) and (1 <= w <= 8):
                    adjacent.add(f"z{d}_{w}")

        # Can stay in same zone
        adjacent.add(zone)

        return adjacent

    @staticmethod
    def is_adjacent(zone1: str, zone2: str) -> bool:
        """Check if two zones are adjacent (or same).

        Args:
            zone1: First zone
            zone2: Second zone

        Returns:
            True if zone2 is adjacent to zone1
        """
        return zone2 in ZoneGraph.get_adjacent_zones(zone1)


class PhysicsValidator:
    """Validate physics-only handball analysis with track IDs and fine-grained zones."""

    VALID_STATES = {"Holding", "Dribbling", "In-Air", "Loose"}
    VALID_TEAMS = {"white", "blue", "unknown", None}

    def __init__(self):
        self.zone_graph = ZoneGraph()
        self.valid_zones = self._generate_valid_zones()

    def _generate_valid_zones(self) -> set[str]:
        """Generate set of all valid zone strings.

        Returns:
            Set of 49 valid zone strings
        """
        zones = {"z0"}  # Goal
        for depth in range(1, 7):  # 6 depth bands
            for lateral in range(1, 9):  # 8 lateral positions
                zones.add(f"z{depth}_{lateral}")
        return zones  # 49 total zones

    def validate_frame(self, frame: dict, frame_idx: int, fps: float) -> list[str]:
        """Validate single frame object.

        Args:
            frame: Frame data dictionary
            frame_idx: Frame index (0-based)
            fps: Frames per second

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # 1. Timestamp Continuity
        expected_ts = frame_idx / fps
        actual_ts = float(frame.get("timestamp", -1))
        if abs(actual_ts - expected_ts) > 0.01:  # 10ms tolerance
            errors.append(
                f"Frame {frame_idx}: Timestamp mismatch "
                f"(expected {expected_ts:.4f}, got {actual_ts:.4f})"
            )

        # 2. Ball Validation
        ball = frame.get("ball", {})
        ball_zone = ball.get("zone")
        if ball_zone not in self.valid_zones:
            errors.append(f"Frame {frame_idx}: Invalid ball zone '{ball_zone}'")

        ball_state = ball.get("state")
        if ball_state not in self.VALID_STATES:
            errors.append(f"Frame {frame_idx}: Invalid ball state '{ball_state}'")

        # 3. Players Validation
        players = frame.get("players", [])
        if not isinstance(players, list):
            errors.append(f"Frame {frame_idx}: 'players' must be an array")
            return errors

        track_ids = set()
        for idx, player in enumerate(players):
            # Track ID required
            track_id = player.get("track_id")
            if not track_id:
                errors.append(f"Frame {frame_idx}, Player {idx}: Missing track_id")
            elif track_id in track_ids:
                errors.append(f"Frame {frame_idx}: Duplicate track_id '{track_id}'")
            else:
                track_ids.add(track_id)

            # Zone validation
            zone = player.get("zone")
            if zone not in self.valid_zones:
                errors.append(f"Frame {frame_idx}, {track_id}: Invalid zone '{zone}'")

            # Team validation (optional field)
            team = player.get("team")
            if team not in self.VALID_TEAMS:
                errors.append(f"Frame {frame_idx}, {track_id}: Invalid team '{team}'")

        # 4. Ball Holder Consistency
        holder_track = ball.get("holder_track_id")
        if holder_track and holder_track not in track_ids:
            errors.append(
                f"Frame {frame_idx}: Ball holder '{holder_track}' not in players list"
            )

        if holder_track:
            # Find holder's zone
            holder_zone = next(
                (p["zone"] for p in players if p.get("track_id") == holder_track),
                None
            )
            if holder_zone and holder_zone != ball_zone:
                errors.append(
                    f"Frame {frame_idx}: Ball zone '{ball_zone}' != "
                    f"holder zone '{holder_zone}' for {holder_track}"
                )

        return errors

    def validate_physics_continuity(self, frames: list[dict], fps: float) -> list[str]:
        """Cross-frame physics validation with adjacency checking.

        Args:
            frames: List of frame data dictionaries
            fps: Frames per second

        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        prev_positions = {}  # track_id -> zone

        for i, frame in enumerate(frames):
            players = frame.get("players", [])

            for player in players:
                track_id = player.get("track_id")
                current_zone = player.get("zone")

                if not track_id or not current_zone:
                    continue

                # Check adjacency constraint
                if track_id in prev_positions:
                    prev_zone = prev_positions[track_id]
                    if not self.zone_graph.is_adjacent(prev_zone, current_zone):
                        errors.append(
                            f"Frame {i}: Player {track_id} violated adjacency - "
                            f"{prev_zone} → {current_zone} (not adjacent at {fps}fps)"
                        )

                prev_positions[track_id] = current_zone

        return errors

    def validate_all(self, data: list[dict], fps: float = 16.0) -> list[str]:
        """Run all validation checks.

        Args:
            data: Full physics JSON (metadata + frames)
            fps: Frames per second (default 16.0)

        Returns:
            List of all error messages
        """
        errors = []

        # Skip metadata frame
        frames = [f for f in data if "timestamp" in f]

        if not frames:
            errors.append("No frames found in data")
            return errors

        # Per-frame validation
        for i, frame in enumerate(frames):
            errors.extend(self.validate_frame(frame, i, fps))

        # Cross-frame validation
        errors.extend(self.validate_physics_continuity(frames, fps))

        return errors


def main():
    """Command-line interface for validation."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python validate_physics_output.py <physics_json_file>")
        sys.exit(1)

    json_path = Path(sys.argv[1])
    if not json_path.exists():
        print(f"Error: File not found: {json_path}")
        sys.exit(1)

    # Load JSON
    with open(json_path) as f:
        data = json.load(f)

    # Validate
    validator = PhysicsValidator()
    errors = validator.validate_all(data)

    # Report results
    if errors:
        print(f"❌ Validation failed with {len(errors)} errors:\n")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✅ Validation passed! All physics constraints satisfied.")
        sys.exit(0)


if __name__ == "__main__":
    main()
