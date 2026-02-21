"""Tests for inference/zone_validator.py — zone adjacency and teleport detection."""

import pytest
from inference.zone_validator import (
    are_adjacent,
    validate_zone_transitions,
    ZONE_ADJACENCY,
)


# ---------------------------------------------------------------------------
# Adjacency map integrity
# ---------------------------------------------------------------------------

class TestAdjacencyMap:
    """Verify the adjacency map is symmetric and complete."""

    def test_all_zones_present(self):
        assert set(ZONE_ADJACENCY.keys()) == set(range(14))

    def test_symmetry(self):
        """If z_a is adjacent to z_b, then z_b must be adjacent to z_a."""
        for za, neighbors in ZONE_ADJACENCY.items():
            for zb in neighbors:
                assert za in ZONE_ADJACENCY[zb], (
                    f"z{za} lists z{zb} as neighbor, but z{zb} does not list z{za}"
                )

    def test_goal_adjacent_to_close_band(self):
        assert ZONE_ADJACENCY[0] == {1, 2, 3, 4, 5}

    def test_deep_zones_not_adjacent_to_close(self):
        for deep in [11, 12, 13]:
            for close in [0, 1, 2, 3, 4, 5]:
                assert not are_adjacent(deep, close), (
                    f"z{deep} should NOT be adjacent to z{close}"
                )


# ---------------------------------------------------------------------------
# are_adjacent()
# ---------------------------------------------------------------------------

class TestAreAdjacent:

    def test_same_zone(self):
        for z in range(14):
            assert are_adjacent(z, z)

    def test_adjacent_pair(self):
        assert are_adjacent(8, 3)  # center back → center close
        assert are_adjacent(12, 8)  # deep center → center back

    def test_non_adjacent_pair(self):
        assert not are_adjacent(12, 3)  # deep center → close center (2 hops)
        assert not are_adjacent(1, 6)   # far left wing → far right back

    def test_wing_to_back(self):
        assert are_adjacent(1, 10)  # LW → far left back
        assert are_adjacent(5, 6)   # RW → far right back

    def test_diagonal_back_to_deep(self):
        assert are_adjacent(7, 13)  # right-center back → deep right
        assert are_adjacent(9, 11)  # left-center back → deep left


# ---------------------------------------------------------------------------
# validate_zone_transitions()
# ---------------------------------------------------------------------------

def _make_frame(ts, players):
    """Build a frame with given players: list of (track_id, zone)."""
    return {
        "timestamp": str(ts),
        "ball": {"holder_track_id": None, "zone": "z0", "state": "Loose"},
        "players": [
            {"track_id": tid, "zone": f"z{z}", "team": "white"}
            for tid, z in players
        ],
    }


class TestValidateZoneTransitions:

    def test_no_warnings_for_adjacent(self):
        frames = [
            _make_frame(0.0, [("t1", 12)]),
            _make_frame(0.5, [("t1", 8)]),
        ]
        assert validate_zone_transitions(frames) == []

    def test_teleport_detected(self):
        """z12→z3 is a teleport (2+ hops)."""
        frames = [
            _make_frame(0.0, [("t1", 12)]),
            _make_frame(0.5, [("t1", 3)]),
        ]
        warnings = validate_zone_transitions(frames)
        assert len(warnings) == 1
        assert warnings[0].track_id == "t1"
        assert warnings[0].zone_from == 12
        assert warnings[0].zone_to == 3

    def test_teleport_z9_to_z3(self):
        """z9→z3 is valid (adjacent), no warning."""
        frames = [
            _make_frame(0.0, [("t1", 9)]),
            _make_frame(0.5, [("t1", 3)]),
        ]
        assert validate_zone_transitions(frames) == []

    def test_multiple_players_mixed(self):
        """Two players: one teleports, one moves normally."""
        frames = [
            _make_frame(0.0, [("t1", 12), ("t2", 8)]),
            _make_frame(0.5, [("t1", 3), ("t2", 9)]),
        ]
        warnings = validate_zone_transitions(frames)
        assert len(warnings) == 1
        assert warnings[0].track_id == "t1"

    def test_static_no_warnings(self):
        frames = [
            _make_frame(0.0, [("t1", 8), ("t2", 3)]),
            _make_frame(0.5, [("t1", 8), ("t2", 3)]),
        ]
        assert validate_zone_transitions(frames) == []

    def test_player_disappears_no_crash(self):
        """Player in frame 0 but not frame 1 — no warning, no crash."""
        frames = [
            _make_frame(0.0, [("t1", 8), ("t2", 3)]),
            _make_frame(0.5, [("t1", 7)]),
        ]
        assert validate_zone_transitions(frames) == []

    def test_gi17_scene_009_regression(self):
        """GI17scenes-Scene-009: t1 goes z9→z9→z3 — the z9→z3 hop is non-adjacent but
        z9 is adjacent to z3 in our map (they share a border via the 8m band edge),
        so no warning. The real issue is z9 should have been z12."""
        frames = [
            _make_frame(0.0, [("t1", 9)]),
            _make_frame(0.5, [("t1", 9)]),
            _make_frame(1.0, [("t1", 3)]),
        ]
        warnings = validate_zone_transitions(frames)
        assert len(warnings) == 0

    def test_warning_to_dict(self):
        frames = [
            _make_frame(0.0, [("t1", 11)]),
            _make_frame(0.5, [("t1", 3)]),
        ]
        warnings = validate_zone_transitions(frames)
        assert len(warnings) == 1
        d = warnings[0].to_dict()
        assert d["type"] == "teleport"
        assert d["track_id"] == "t1"
        assert d["zone_from"] == 11
        assert d["zone_to"] == 3
