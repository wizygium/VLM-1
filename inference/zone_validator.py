"""
Zone adjacency validation for the 14-zone handball court system.

Detects "teleports" — players jumping between non-adjacent zones in a single
frame interval — and reports them as warnings.

Zone layout (attacker's perspective, facing goal):
```
              10m+ from goal (Deep Court)
         [ z13 ]    [ z12 ]    [ z11 ]

         ╭────── 8m-10m (Backcourt) ──────╮
         [ z6 ] [ z7 ] [ z8 ] [ z9 ] [ z10]

         ╭────── 6m-9m (Close Attack) ────╮
         [ z5 ] [ z4 ] [ z3 ] [ z2 ] [ z1 ]

         \\__________ GOAL (z0) __________/
```
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Set

ZONE_ADJACENCY: Dict[int, Set[int]] = {
    0:  {1, 2, 3, 4, 5},
    1:  {0, 2, 9, 10},
    2:  {0, 1, 3, 8, 9, 10},
    3:  {0, 2, 4, 7, 8, 9},
    4:  {0, 3, 5, 6, 7, 8},
    5:  {0, 4, 6, 7},
    6:  {5, 4, 7, 13},
    7:  {3, 4, 5, 6, 8, 12, 13},
    8:  {2, 3, 4, 7, 9, 11, 12, 13},
    9:  {1, 2, 3, 8, 10, 11, 12},
    10: {1, 2, 9, 11},
    11: {9, 10, 12, 8},
    12: {7, 8, 9, 11, 13},
    13: {6, 7, 8, 12},
}


def normalize_zone(zone: Any) -> int:
    if isinstance(zone, int):
        return zone
    if isinstance(zone, str):
        return int(zone.replace("z", ""))
    return 0


def are_adjacent(z_a: int, z_b: int) -> bool:
    """Check if two zones are adjacent (or the same)."""
    if z_a == z_b:
        return True
    return z_b in ZONE_ADJACENCY.get(z_a, set())


@dataclass
class ZoneWarning:
    timestamp_from: str
    timestamp_to: str
    track_id: str
    zone_from: int
    zone_to: int
    team: str = ""

    def __str__(self) -> str:
        return (
            f"Teleport: {self.track_id} z{self.zone_from}→z{self.zone_to} "
            f"({self.timestamp_from}s→{self.timestamp_to}s)"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "teleport",
            "track_id": self.track_id,
            "zone_from": self.zone_from,
            "zone_to": self.zone_to,
            "timestamp_from": self.timestamp_from,
            "timestamp_to": self.timestamp_to,
        }


def validate_zone_transitions(frames: List[Dict]) -> List[ZoneWarning]:
    """Check all player zone transitions across consecutive frames.

    Returns a list of ZoneWarning for any non-adjacent zone jump.
    """
    warnings: List[ZoneWarning] = []

    for i in range(len(frames) - 1):
        frame_a = frames[i]
        frame_b = frames[i + 1]
        ts_a = str(frame_a.get("timestamp", ""))
        ts_b = str(frame_b.get("timestamp", ""))

        players_a = {p["track_id"]: p for p in frame_a.get("players", [])}
        players_b = {p["track_id"]: p for p in frame_b.get("players", [])}

        for tid, pa in players_a.items():
            if tid not in players_b:
                continue
            pb = players_b[tid]
            za = normalize_zone(pa.get("zone", 0))
            zb = normalize_zone(pb.get("zone", 0))

            if not are_adjacent(za, zb):
                warnings.append(ZoneWarning(
                    timestamp_from=ts_a,
                    timestamp_to=ts_b,
                    track_id=tid,
                    zone_from=za,
                    zone_to=zb,
                    team=pa.get("team", ""),
                ))

    return warnings
