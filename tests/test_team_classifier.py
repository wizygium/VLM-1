"""Tests for inference/team_classifier.py — multi-signal team classification.

Covers all 12 test cases from issue #32:
  TC-T1:  Ball possession determines attacking team
  TC-T2:  Goalkeeper in z0 with unique colour
  TC-T3:  No goalkeeper visible (7v6 attack or off-camera)
  TC-T4:  Defensive wall formation detection
  TC-T5:  Zone depth signal
  TC-T6:  Transition / even possession
  TC-T7:  No ball holder in any frame
  TC-T8:  Explicit "attack"/"defense" labels (backward compat)
  TC-T9:  JDF-Scene-001 regression
  TC-T10: Signals disagree (stress test)
  TC-T11: Single frame
  TC-T12: Three-team colours with GK association
"""

import json
import pytest
from pathlib import Path

from inference.team_classifier import (
    determine_attacking_team,
    TeamClassification,
    _signal_possession,
    _signal_gk_spatial,
    _signal_zone_depth,
    _signal_formation,
    _get_field_teams_and_gk,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _player(track_id, zone, team):
    return {"track_id": track_id, "zone": f"z{zone}", "jersey_number": None, "team": team}


def _frame(ts, holder, ball_zone, ball_state, players):
    return {
        "timestamp": str(ts),
        "ball": {
            "holder_track_id": holder,
            "zone": f"z{ball_zone}",
            "state": ball_state,
        },
        "players": players,
    }


# ---------------------------------------------------------------------------
# Reusable player sets
# ---------------------------------------------------------------------------

# White attacking from backcourt, blue defending on 6m wall, yellow GK
WHITE_ATTACKERS = [
    _player("t1", 7, "white"),   # LCB
    _player("t2", 8, "white"),   # CB
    _player("t3", 9, "white"),   # RCB
    _player("t4", 3, "white"),   # Pivot
    _player("t5", 1, "white"),   # RW
    _player("t6", 5, "white"),   # LW
]
BLUE_DEFENDERS = [
    _player("t8", 1, "blue"),
    _player("t9", 2, "blue"),
    _player("t10", 3, "blue"),
    _player("t11", 4, "blue"),
    _player("t12", 5, "blue"),
]
YELLOW_GK = [_player("t7", 0, "yellow")]

ALL_JDF_PLAYERS = WHITE_ATTACKERS + YELLOW_GK + BLUE_DEFENDERS


# ===========================================================================
# A. Ball Possession Signal
# ===========================================================================

class TestBallPossessionSignal:
    """TC-T1, TC-T6, TC-T7."""

    def test_dominant_possession(self):
        """TC-T1: White holds ball in every frame → white = attacking."""
        frames = [
            _frame(0.0, "t1", 7, "Holding", ALL_JDF_PLAYERS),
            _frame(0.5, "t2", 8, "Holding", ALL_JDF_PLAYERS),
            _frame(1.0, "t1", 7, "Holding", ALL_JDF_PLAYERS),
        ]
        result = determine_attacking_team(frames)
        assert result.attacking_team == "white"
        assert result.defending_team == "blue"
        assert result.confidence > 0.3

    def test_even_possession(self):
        """TC-T6: Nearly equal possession → still picks majority holder, lower confidence."""
        # Use balanced positions so only possession differentiates
        balanced_players = [
            _player("w1", 7, "white"), _player("w2", 3, "white"),
            _player("b1", 8, "blue"), _player("b2", 2, "blue"),
            _player("gk", 0, "yellow"),
        ]
        frames = [
            _frame(0.0, "w1", 7, "Holding", balanced_players),
            _frame(0.5, "b1", 8, "Holding", balanced_players),
            _frame(1.0, "w2", 3, "Holding", balanced_players),
            _frame(1.5, "b2", 2, "Holding", balanced_players),
            _frame(2.0, "w1", 7, "Holding", balanced_players),
        ]
        result = determine_attacking_team(frames)
        # White holds 3/5, blue holds 2/5 — white has majority
        assert result.attacking_team == "white"
        # Confidence should be low because positions are balanced
        assert result.confidence < 0.15

    def test_no_holder_any_frame(self):
        """TC-T7: No ball holder → possession signal is zero, depth/formation decide."""
        frames = [
            _frame(0.0, None, 5, "Loose", ALL_JDF_PLAYERS),
            _frame(0.5, None, 6, "Loose", ALL_JDF_PLAYERS),
            _frame(1.0, None, 7, "Loose", ALL_JDF_PLAYERS),
        ]
        result = determine_attacking_team(frames)
        # Depth and formation signals should still identify white as attacking
        # (white avg depth ~7.7, blue avg depth ~3.0)
        assert result.attacking_team == "white"
        assert result.defending_team == "blue"


# ===========================================================================
# B. Goalkeeper Signal
# ===========================================================================

class TestGoalkeeperSignal:
    """TC-T2, TC-T3, TC-T12."""

    def test_gk_unique_colour(self):
        """TC-T2: Yellow GK in z0 → detected; blue nearest to GK = defending."""
        frames = [
            _frame(0.0, "t1", 7, "Holding", ALL_JDF_PLAYERS),
        ]
        field_teams, gk_team = _get_field_teams_and_gk(frames)
        assert gk_team == "yellow"
        assert "white" in field_teams
        assert "blue" in field_teams
        assert "yellow" not in field_teams

        # GK spatial signal: blue should get lower attack score (nearer to GK)
        sig = _signal_gk_spatial(frames, field_teams, gk_team)
        assert sig["white"] > sig["blue"]

    def test_no_gk_visible(self):
        """TC-T3: No player in z0 → GK signal inactive."""
        players_no_gk = WHITE_ATTACKERS + BLUE_DEFENDERS  # No yellow GK
        frames = [
            _frame(0.0, "t1", 7, "Holding", players_no_gk),
        ]
        field_teams, gk_team = _get_field_teams_and_gk(frames)
        assert gk_team is None
        assert "white" in field_teams
        assert "blue" in field_teams

        # GK spatial signal should be empty (inactive)
        sig = _signal_gk_spatial(frames, field_teams, None)
        assert sig == {}

        # Full classification should still work via other signals
        result = determine_attacking_team(frames)
        assert result.attacking_team == "white"
        assert result.goalkeeper_team is None

    def test_three_colours_gk_association(self):
        """TC-T12: Three colours — yellow GK correctly identified and excluded."""
        frames = [
            _frame(0.0, "t1", 7, "Holding", ALL_JDF_PLAYERS),
            _frame(0.5, "t2", 8, "Holding", ALL_JDF_PLAYERS),
        ]
        result = determine_attacking_team(frames)
        assert result.goalkeeper_team == "yellow"
        assert result.attacking_team == "white"
        assert result.defending_team == "blue"


# ===========================================================================
# C. Zone Depth Signal
# ===========================================================================

class TestZoneDepthSignal:
    """TC-T5."""

    def test_backcourt_vs_6m(self):
        """TC-T5: Team in z6-z10 (9m avg) deeper than team in z1-z5 (7m avg)."""
        frames = [
            _frame(0.0, None, 7, "Loose", ALL_JDF_PLAYERS),
        ]
        sig = _signal_zone_depth(frames, {"white", "blue"})
        # White has players in z7, z8, z9 (depth 9m) plus z3, z1, z5 (7m)
        # → avg ≈ 8.0
        # Blue has all players in z1-z5 (7m) → avg = 7.0
        assert sig["white"] > sig["blue"]

    def test_equal_depth_neutral(self):
        """Both teams at same average depth → scores are 0.5."""
        players = [
            _player("a1", 8, "red"),
            _player("b1", 8, "green"),
        ]
        frames = [_frame(0.0, None, 8, "Loose", players)]
        sig = _signal_zone_depth(frames, {"red", "green"})
        assert sig["red"] == pytest.approx(0.5)
        assert sig["green"] == pytest.approx(0.5)


# ===========================================================================
# D. Defensive Formation Signal
# ===========================================================================

class TestFormationSignal:
    """TC-T4."""

    def test_wall_detection(self):
        """TC-T4: 5 blue players in z1-z5 = defensive wall → low attack score."""
        frames = [
            _frame(0.0, "t1", 7, "Holding", ALL_JDF_PLAYERS),
        ]
        sig = _signal_formation(frames, {"white", "blue"})
        # Blue: 5/5 in z1-z5 → ratio 1.0 → attack score 0.0
        # White: 3/6 in z1-z5 (t4@z3, t5@z1, t6@z5) → ratio 0.5 → higher attack score
        assert sig["white"] > sig["blue"]

    def test_no_wall(self):
        """Both teams spread across court → similar formation scores."""
        players = [
            _player("a1", 7, "red"), _player("a2", 3, "red"),
            _player("b1", 8, "green"), _player("b2", 2, "green"),
        ]
        frames = [_frame(0.0, None, 7, "Loose", players)]
        sig = _signal_formation(frames, {"red", "green"})
        # Both have 50% in z1-z5 → equal scores
        assert sig["red"] == pytest.approx(0.5)
        assert sig["green"] == pytest.approx(0.5)


# ===========================================================================
# E. Explicit Labels (Backward Compatibility)
# ===========================================================================

class TestExplicitLabels:
    """TC-T8."""

    def test_attack_defense_labels(self):
        """TC-T8: Explicit 'attack'/'defense' labels → used directly."""
        players = [
            _player("a1", 7, "attack"),
            _player("d1", 3, "defense"),
        ]
        frames = [_frame(0.0, "a1", 7, "Holding", players)]
        result = determine_attacking_team(frames)
        assert result.attacking_team == "attack"
        assert result.defending_team == "defense"
        assert result.confidence == 1.0
        assert result.signals.get("explicit_labels") is True


# ===========================================================================
# F. Combined Scoring / Integration
# ===========================================================================

class TestCombinedScoring:
    """TC-T9, TC-T10, TC-T11."""

    def test_jdf_scene_001_regression(self):
        """TC-T9: Real JDF-Scene-001 data → white=attacking, blue=defending."""
        p = Path("data/analyses/JDF-Scene-001_physics.json")
        if not p.exists():
            pytest.skip("JDF-Scene-001_physics.json not available")

        with open(p) as f:
            data = json.load(f)

        result = determine_attacking_team(data["frames"])
        assert result.attacking_team == "white", (
            f"Expected white=attacking, got {result.attacking_team} "
            f"(scores: {result.signals.get('scores')})"
        )
        assert result.defending_team == "blue"
        assert result.goalkeeper_team == "yellow"
        assert result.confidence > 0.2

        # Verify all ball holders (t1, t2, t3, t6) are on the attacking team
        ball_holders = set()
        for frame in data["frames"]:
            h = frame["ball"].get("holder_track_id")
            if h:
                ball_holders.add(h)
        # All holders should be white team
        for holder in ball_holders:
            for frame in data["frames"]:
                for p_data in frame["players"]:
                    if p_data["track_id"] == holder:
                        assert p_data["team"] == "white", (
                            f"Ball holder {holder} is {p_data['team']}, not white"
                        )
                        break
                break

    def test_signals_disagree(self):
        """TC-T10: Ball possession contradicts depth+formation → possession wins."""
        # Red holds ball (possession signal → red=attacking)
        # But red is at z3 (shallow) and green is at z9 (deep)
        # → depth+formation both say green=attacking
        # Possession weight (0.55) must override depth+formation (0.25+0.20=0.45)
        players = [
            _player("r1", 3, "red"),
            _player("r2", 2, "red"),
            _player("g1", 9, "green"),
            _player("g2", 10, "green"),
        ]
        frames = [
            _frame(0.0, "r1", 3, "Holding", players),
            _frame(0.5, "r2", 2, "Holding", players),
            _frame(1.0, "r1", 3, "Holding", players),
        ]
        result = determine_attacking_team(frames)
        # Possession (weight 0.55 no-GK) overcomes depth (0.25) + formation (0.20)
        assert result.attacking_team == "red"
        assert result.defending_team == "green"

    def test_single_frame(self):
        """TC-T11: Single frame → still produces a determination."""
        frames = [
            _frame(0.0, "t1", 7, "Holding", ALL_JDF_PLAYERS),
        ]
        result = determine_attacking_team(frames)
        assert result.attacking_team == "white"
        assert result.defending_team == "blue"
        assert result.confidence > 0

    def test_empty_frames(self):
        """No frames → graceful fallback."""
        result = determine_attacking_team([])
        assert result.attacking_team == "unknown"
        assert result.defending_team == "unknown"
        assert result.confidence == 0.0

    def test_only_one_field_team(self):
        """Single team colour → attacking by default, defending=unknown."""
        players = [_player("t1", 7, "red"), _player("t2", 8, "red")]
        frames = [_frame(0.0, "t1", 7, "Holding", players)]
        result = determine_attacking_team(frames)
        assert result.attacking_team == "red"
        assert result.defending_team == "unknown"

    def test_gk_same_colour_as_field_team(self):
        """GK in z0 with same colour as a field team → no GK detection."""
        # Blue GK in z0 + blue defenders → blue appears in z0 AND z1-z5
        # → z0 ratio < 0.8 for blue → no GK detected → all are field teams
        players = [
            _player("gk", 0, "blue"),   # Blue GK
            _player("d1", 2, "blue"),
            _player("d2", 3, "blue"),
            _player("d3", 4, "blue"),
            _player("a1", 8, "white"),
            _player("a2", 9, "white"),
        ]
        frames = [
            _frame(0.0, "a1", 8, "Holding", players),
            _frame(0.5, "a2", 9, "Holding", players),
        ]
        result = determine_attacking_team(frames)
        # No GK detected (blue is in both z0 and field)
        assert result.goalkeeper_team is None
        # White should still be attacking (possession + depth)
        assert result.attacking_team == "white"
        assert result.defending_team == "blue"


# ===========================================================================
# G. Field Teams / GK Identification Edge Cases
# ===========================================================================

class TestFieldTeamIdentification:
    """Additional edge cases for _get_field_teams_and_gk."""

    def test_gk_appears_in_z0_all_frames(self):
        """GK that is 100% in z0 → correctly detected."""
        players = [
            _player("gk", 0, "yellow"),
            _player("a1", 8, "white"),
            _player("d1", 3, "blue"),
        ]
        frames = [
            _frame(0.0, "a1", 8, "Holding", players),
            _frame(0.5, "a1", 8, "Holding", players),
        ]
        field_teams, gk = _get_field_teams_and_gk(frames)
        assert gk == "yellow"
        assert field_teams == {"white", "blue"}

    def test_gk_briefly_leaves_z0(self):
        """GK in z0 for 90% of frames (leaves once) → still detected as GK."""
        base_players = [
            _player("a1", 8, "white"),
            _player("d1", 3, "blue"),
        ]
        frames = []
        # 9 frames with GK in z0
        for i in range(9):
            frames.append(_frame(
                i * 0.5, "a1", 8, "Holding",
                base_players + [_player("gk", 0, "yellow")]
            ))
        # 1 frame with GK in z1 (came out to play ball)
        frames.append(_frame(
            4.5, "a1", 8, "Holding",
            base_players + [_player("gk", 1, "yellow")]
        ))

        field_teams, gk = _get_field_teams_and_gk(frames)
        assert gk == "yellow"  # 90% in z0 ≥ 80% threshold
        assert "yellow" not in field_teams
