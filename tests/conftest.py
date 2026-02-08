"""Shared fixtures for physics-to-events tests."""

import pytest


@pytest.fixture
def build_physics_json():
    """Factory to create minimal physics JSON for testing.

    Usage:
        data = build_physics_json(frames=[
            (0.0, "t1", 7, "Holding", [("t1", 7, "white"), ("t2", 8, "white")]),
            (0.5, None, 7, "In-Air", [("t1", 7, "white"), ("t2", 8, "white")]),
            (1.0, "t2", 8, "Holding", [("t1", 7, "white"), ("t2", 8, "white")]),
        ])

    Each frame tuple: (timestamp, holder_track_id, ball_zone, ball_state, players)
    Each player tuple: (track_id, zone, team)
    """
    def _build(frames, video="test.mp4", model="test"):
        physics_frames = []
        for ts, holder, bzone, bstate, players in frames:
            physics_frames.append({
                "timestamp": str(ts),
                "ball": {
                    "holder_track_id": holder,
                    "zone": f"z{bzone}",
                    "state": bstate,
                },
                "players": [
                    {
                        "track_id": tid,
                        "zone": f"z{z}",
                        "jersey_number": None,
                        "team": tm,
                    }
                    for tid, z, tm in players
                ],
            })
        return {
            "metadata": {
                "video": video,
                "model": model,
                "fps": 16.0,
                "total_frames": len(physics_frames),
                "duration_seconds": len(physics_frames) / 16.0,
            },
            "frames": physics_frames,
        }
    return _build


# --- Reusable player lists ---

PLAYERS_TWO_WHITE = [("t1", 7, "white"), ("t2", 8, "white")]
PLAYERS_THREE_WHITE = [("t1", 7, "white"), ("t2", 8, "white"), ("t3", 9, "white")]
PLAYERS_MIXED = [
    ("t1", 7, "white"), ("t2", 8, "white"),
    ("t8", 1, "blue"), ("t9", 2, "blue"),
]
