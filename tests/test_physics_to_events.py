"""Integration tests for physics_to_events.py end-to-end pipeline."""

import json
import pytest
from pathlib import Path

from physics_to_events import transform_physics_to_events, parse_physics_json


# ===========================================================================
# F. Integration / End-to-End
# ===========================================================================

class TestJDFScene001Regression:
    """TC-F1: JDF-Scene-001 regression test against real physics data."""

    @pytest.fixture
    def jdf_physics_path(self):
        p = Path("data/analyses/JDF-Scene-001_physics.json")
        if not p.exists():
            pytest.skip("JDF-Scene-001_physics.json not available")
        return p

    def test_passes_detected(self, jdf_physics_path):
        """At least 4 PASS events should be detected from JDF-Scene-001."""
        physics = parse_physics_json(jdf_physics_path)
        result = transform_physics_to_events(physics, jdf_physics_path)
        passes = [e for e in result["events"] if e["type"] == "PASS"]
        assert len(passes) >= 4, (
            f"Expected >=4 passes, got {len(passes)}. "
            f"Events: {[e['type'] for e in result['events']]}"
        )

    def test_no_incorrect_rw_for_z4(self, jdf_physics_path):
        """No player in z4 (left-center) should be assigned RW."""
        physics = parse_physics_json(jdf_physics_path)
        result = transform_physics_to_events(physics, jdf_physics_path)
        for team in result["roster"].values():
            for player in team:
                if player["role"] == "RW":
                    # Check the player's zone in frame 0
                    frame0 = result["frames"][0]
                    for fp in frame0["players"]:
                        if fp["track_id"] == player["track_id"]:
                            zone = int(fp["zone"].replace("z", ""))
                            assert zone != 4, (
                                f"Player {player['track_id']} in z4 was assigned RW"
                            )

    def test_output_structure(self, jdf_physics_path):
        """Output has required top-level keys."""
        physics = parse_physics_json(jdf_physics_path)
        result = transform_physics_to_events(physics, jdf_physics_path)
        assert "metadata" in result
        assert "roster" in result
        assert "events" in result
        assert "frames" in result
        assert "attack" in result["roster"]
        assert "defense" in result["roster"]

    def test_enriched_frames_have_roles(self, jdf_physics_path):
        """Every player in enriched frames should have a 'role' field."""
        physics = parse_physics_json(jdf_physics_path)
        result = transform_physics_to_events(physics, jdf_physics_path)
        for frame in result["frames"]:
            for player in frame["players"]:
                assert "role" in player, (
                    f"Player {player['track_id']} in frame {frame['timestamp']} "
                    f"missing 'role' field"
                )

    def test_white_team_is_attacking(self, jdf_physics_path):
        """Issue #32 regression: white team must be classified as attackers."""
        physics = parse_physics_json(jdf_physics_path)
        result = transform_physics_to_events(physics, jdf_physics_path)
        tc = result["metadata"].get("team_classification", {})
        assert tc.get("attacking_team") == "white", (
            f"Expected white=attacking, got {tc}"
        )
        assert tc.get("defending_team") == "blue"
        assert tc.get("goalkeeper_team") == "yellow"

        # All ball holders (t1, t2, t3, t6) must be in the attack roster
        attack_ids = {p["track_id"] for p in result["roster"]["attack"]}
        assert {"t1", "t2", "t3", "t6"}.issubset(attack_ids), (
            f"Ball holders not all in attack roster: {attack_ids}"
        )

    def test_attackers_get_attack_roles(self, jdf_physics_path):
        """White attackers should get attacking roles (LW/RW/PV/LB/CB/RB)."""
        physics = parse_physics_json(jdf_physics_path)
        result = transform_physics_to_events(physics, jdf_physics_path)
        attack_roles = {p["role"] for p in result["roster"]["attack"]}
        defense_roles = {p["role"] for p in result["roster"]["defense"]}
        # Attack roles should contain at least some of LW, RW, LB, CB, RB, PV
        attack_role_set = {"LW", "RW", "PV", "LB", "CB", "RB"}
        assert len(attack_roles & attack_role_set) >= 3, (
            f"Too few attacking roles: {attack_roles}"
        )
        # Defense roles should be DL1-DR1
        defense_role_set = {"DL1", "DL2", "DL3", "DR3", "DR2", "DR1"}
        assert len(defense_roles & defense_role_set) >= 3, (
            f"Too few defensive roles: {defense_roles}"
        )


class TestEdgeCases:
    """TC-F2, F3: Edge cases for the pipeline."""

    def test_empty_frames(self, build_physics_json):
        """TC-F2: Empty frames → 0 events, no crash."""
        data = build_physics_json(frames=[])
        result = transform_physics_to_events(data, Path("test.json"))
        assert result["events"] == []
        assert result["frames"] == []
        assert result["roster"]["attack"] == []
        assert result["roster"]["defense"] == []

    def test_single_frame(self, build_physics_json):
        """TC-F3: 1 frame → 0 events (need 2 frames), roster still built."""
        data = build_physics_json(frames=[
            (0.0, "t1", 7, "Holding", [("t1", 7, "white"), ("t8", 1, "blue")]),
        ])
        result = transform_physics_to_events(data, Path("test.json"))
        assert result["events"] == []
        assert len(result["frames"]) == 1
        # Roster should still be populated
        total_roster = len(result["roster"]["attack"]) + len(result["roster"]["defense"])
        assert total_roster > 0


class TestEventTimestamps:
    """Verify event timestamps are correct strings/floats."""

    def test_pass_timestamps(self, build_physics_json):
        """PASS start_time and end_time match the frame timestamps."""
        data = build_physics_json(frames=[
            (0.5, "t1", 7, "Holding", [("t1", 7, "white"), ("t2", 8, "white")]),
            (1.0, None, 7, "In-Air", [("t1", 7, "white"), ("t2", 8, "white")]),
            (1.5, "t2", 8, "Holding", [("t1", 7, "white"), ("t2", 8, "white")]),
        ])
        result = transform_physics_to_events(data, Path("test.json"))
        passes = [e for e in result["events"] if e["type"] == "PASS"]
        assert len(passes) == 1
        # start_time = when t1 was last holding (0.5)
        # end_time = when t2 catches (1.5)
        assert float(passes[0]["start_time"]) == pytest.approx(0.5, abs=0.01)
        assert float(passes[0]["end_time"]) == pytest.approx(1.5, abs=0.01)
