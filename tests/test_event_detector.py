"""Tests for inference/event_detector.py — pass, shot, turnover, and move detection."""

import pytest
from inference.event_detector import EventDetector, EventType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_frame(ts, holder, zone, state, players=None):
    """Build a minimal physics frame dict."""
    return {
        "timestamp": str(ts),
        "ball": {
            "holder_track_id": holder,
            "zone": f"z{zone}",
            "state": state,
        },
        "players": players or [],
    }


def _run_detector(frames, attacker_ids=None, defender_ids=None, roles=None):
    """Run EventDetector across a list of frames, return all events."""
    roles = roles or {}
    detector = EventDetector(
        roles,
        attacker_ids=attacker_ids or set(),
        defender_ids=defender_ids or set(),
    )
    all_events = []
    for i in range(len(frames) - 1):
        is_last = i == len(frames) - 2
        evts = detector.detect_all_events(frames[i], frames[i + 1], is_last_frame=is_last)
        all_events.extend(evts)
    return all_events


def _events_of_type(events, etype):
    return [e for e in events if e.type == etype]


# ===========================================================================
# A. Pass Detection
# ===========================================================================

class TestPassDetection:
    """TC-A*: Pass detection with state machine."""

    def test_pass_via_in_air_same_team(self):
        """TC-A1: Holding(t1) → In-Air → Holding(t2), both white → 1 PASS."""
        frames = [
            _make_frame(0.0, "t1", 7, "Holding"),
            _make_frame(0.5, None, 7, "In-Air"),
            _make_frame(1.0, "t2", 8, "Holding"),
        ]
        events = _run_detector(frames, defender_ids={"t1", "t2"})
        passes = _events_of_type(events, EventType.PASS)
        assert len(passes) == 1
        assert passes[0].from_track_id == "t1"
        assert passes[0].to_track_id == "t2"
        assert passes[0].from_zone == 7
        assert passes[0].to_zone == 8

    def test_direct_transfer_pass(self):
        """TC-A2: Holding(t1) → Holding(t2) direct, same team → 1 PASS."""
        frames = [
            _make_frame(0.0, "t1", 8, "Holding"),
            _make_frame(0.5, "t2", 9, "Holding"),
        ]
        events = _run_detector(frames, defender_ids={"t1", "t2"})
        passes = _events_of_type(events, EventType.PASS)
        assert len(passes) == 1
        assert passes[0].from_track_id == "t1"
        assert passes[0].to_track_id == "t2"

    def test_pass_chain(self):
        """TC-A3: t1→In-Air→t2→t3→In-Air→t1 → 3 PASS events."""
        frames = [
            _make_frame(0.0, "t1", 7, "Holding"),
            _make_frame(0.5, None, 7, "In-Air"),
            _make_frame(1.0, "t2", 8, "Holding"),
            _make_frame(1.5, "t3", 9, "Holding"),
            _make_frame(2.0, None, 9, "In-Air"),
            _make_frame(2.5, "t1", 7, "Holding"),
        ]
        events = _run_detector(frames, defender_ids={"t1", "t2", "t3"})
        passes = _events_of_type(events, EventType.PASS)
        assert len(passes) == 3
        assert passes[0].from_track_id == "t1" and passes[0].to_track_id == "t2"
        assert passes[1].from_track_id == "t2" and passes[1].to_track_id == "t3"
        assert passes[2].from_track_id == "t3" and passes[2].to_track_id == "t1"

    def test_self_catch_no_pass(self):
        """TC-A4: Holding(t1) → In-Air → Holding(t1) → 0 PASS (self-catch)."""
        frames = [
            _make_frame(0.0, "t1", 7, "Holding"),
            _make_frame(0.5, None, 7, "In-Air"),
            _make_frame(1.0, "t1", 7, "Holding"),
        ]
        events = _run_detector(frames, defender_ids={"t1"})
        passes = _events_of_type(events, EventType.PASS)
        assert len(passes) == 0

    def test_pass_between_attackers(self):
        """TC-A5: Pass between blue team (attacker) players → 1 PASS."""
        frames = [
            _make_frame(0.0, "t8", 1, "Holding"),
            _make_frame(0.5, None, 2, "In-Air"),
            _make_frame(1.0, "t9", 2, "Holding"),
        ]
        events = _run_detector(frames, attacker_ids={"t8", "t9"})
        passes = _events_of_type(events, EventType.PASS)
        assert len(passes) == 1
        assert passes[0].from_track_id == "t8"
        assert passes[0].to_track_id == "t9"

    def test_long_in_air_sequence(self):
        """TC-A6: Holding(t1) → In-Air × 3 → Holding(t2) → 1 PASS."""
        frames = [
            _make_frame(0.0, "t1", 7, "Holding"),
            _make_frame(0.5, None, 7, "In-Air"),
            _make_frame(1.0, None, 6, "In-Air"),
            _make_frame(1.5, None, 5, "In-Air"),
            _make_frame(2.0, "t2", 5, "Holding"),
        ]
        events = _run_detector(frames, defender_ids={"t1", "t2"})
        passes = _events_of_type(events, EventType.PASS)
        assert len(passes) == 1
        assert passes[0].from_track_id == "t1"
        assert passes[0].to_track_id == "t2"
        assert passes[0].from_zone == 7
        assert passes[0].to_zone == 5

    def test_pass_unknown_teams(self):
        """Passes detected even when no team info (both IDs in neither set)."""
        frames = [
            _make_frame(0.0, "t1", 7, "Holding"),
            _make_frame(0.5, "t2", 8, "Holding"),
        ]
        # No attacker_ids or defender_ids
        events = _run_detector(frames)
        passes = _events_of_type(events, EventType.PASS)
        assert len(passes) == 1


# ===========================================================================
# B. Shot Detection
# ===========================================================================

class TestShotDetection:
    """TC-B*: Shot into goal zone detection."""

    def test_shot_into_goal_zone(self):
        """TC-B1: Ball moves from z3 to z0 → 1 SHOT ON_TARGET."""
        frames = [
            _make_frame(0.0, "t1", 3, "Holding"),
            _make_frame(0.5, None, 0, "In-Air"),
        ]
        events = _run_detector(frames)
        shots = _events_of_type(events, EventType.SHOT)
        assert len(shots) == 1
        assert shots[0].from_zone == 3
        assert shots[0].outcome == "ON_TARGET"
        assert shots[0].from_track_id == "t1"

    def test_shot_goal_outcome(self):
        """TC-B2: Ball enters z0 with state containing 'Goal' → GOAL outcome."""
        frames = [
            _make_frame(0.0, "t1", 3, "Holding"),
            _make_frame(0.5, None, 0, "Goal"),
        ]
        events = _run_detector(frames)
        shots = _events_of_type(events, EventType.SHOT)
        assert len(shots) == 1
        assert shots[0].outcome == "GOAL"

    def test_shot_save_outcome(self):
        """TC-B3: Ball enters z0 with state containing 'Save' → SAVE outcome."""
        frames = [
            _make_frame(0.0, "t1", 3, "Holding"),
            _make_frame(0.5, None, 0, "Save"),
        ]
        events = _run_detector(frames)
        shots = _events_of_type(events, EventType.SHOT)
        assert len(shots) == 1
        assert shots[0].outcome == "SAVE"


# ===========================================================================
# C. Turnover / Lost Ball Detection
# ===========================================================================

class TestTurnoverDetection:
    """TC-C*: Turnover, steal, and lost ball detection."""

    def test_steal_cross_team(self):
        """TC-C1: Attacker holds → defender holds → TURNOVER (STEAL)."""
        frames = [
            _make_frame(0.0, "t8", 3, "Holding"),
            _make_frame(0.5, "t1", 3, "Holding"),
        ]
        events = _run_detector(
            frames, attacker_ids={"t8"}, defender_ids={"t1"}
        )
        turnovers = _events_of_type(events, EventType.TURNOVER)
        assert len(turnovers) == 1
        assert turnovers[0].turnover_type == "STEAL"
        assert turnovers[0].from_track_id == "t8"
        assert turnovers[0].to_track_id == "t1"

    def test_out_of_bounds(self):
        """TC-C2: Ball state → 'Out' → TURNOVER (OUT_OF_BOUNDS)."""
        frames = [
            _make_frame(0.0, "t1", 7, "Holding"),
            _make_frame(0.5, None, 7, "Out"),
        ]
        events = _run_detector(frames)
        turnovers = _events_of_type(events, EventType.TURNOVER)
        assert len(turnovers) == 1
        assert turnovers[0].turnover_type == "OUT_OF_BOUNDS"
        assert turnovers[0].from_track_id == "t1"

    def test_loose_ball(self):
        """TC-C3: Holding → In-Air → Loose → TURNOVER (LOST_BALL)."""
        frames = [
            _make_frame(0.0, "t1", 7, "Holding"),
            _make_frame(0.5, None, 6, "In-Air"),
            _make_frame(1.0, None, 5, "Loose"),
        ]
        events = _run_detector(frames)
        turnovers = _events_of_type(events, EventType.TURNOVER)
        assert len(turnovers) == 1
        assert turnovers[0].turnover_type == "LOST_BALL"
        assert turnovers[0].from_track_id == "t1"

    def test_in_air_end_of_clip(self):
        """TC-C4: Holding → In-Air (clip ends) → no crash, no false PASS."""
        frames = [
            _make_frame(0.0, "t1", 7, "Holding"),
            _make_frame(0.5, None, 6, "In-Air"),
        ]
        events = _run_detector(frames)
        passes = _events_of_type(events, EventType.PASS)
        turnovers = _events_of_type(events, EventType.TURNOVER)
        assert len(passes) == 0
        assert len(turnovers) == 0


# ===========================================================================
# E. Move Detection
# ===========================================================================

class TestMoveDetection:
    """TC-E*: Player zone-change MOVE detection."""

    def test_single_move(self):
        """TC-E1: Player changes zone → 1 MOVE event."""
        players_f0 = [{"track_id": "t1", "zone": "z7", "jersey_number": None, "team": "white"}]
        players_f1 = [{"track_id": "t1", "zone": "z8", "jersey_number": None, "team": "white"}]
        frame0 = {"timestamp": "0.0", "ball": {"holder_track_id": "t1", "zone": "z7", "state": "Holding"}, "players": players_f0}
        frame1 = {"timestamp": "0.5", "ball": {"holder_track_id": "t1", "zone": "z8", "state": "Holding"}, "players": players_f1}

        detector = EventDetector({})
        events = detector.detect_all_events(frame0, frame1)
        moves = _events_of_type(events, EventType.MOVE)
        assert len(moves) == 1
        assert moves[0].from_zone == 7
        assert moves[0].to_zone == 8

    def test_no_move_on_static(self):
        """TC-E2: All players stay in same zones → 0 MOVE."""
        players = [{"track_id": "t1", "zone": "z7", "jersey_number": None, "team": "white"}]
        frame0 = {"timestamp": "0.0", "ball": {"holder_track_id": "t1", "zone": "z7", "state": "Holding"}, "players": players}
        frame1 = {"timestamp": "0.5", "ball": {"holder_track_id": "t1", "zone": "z7", "state": "Holding"}, "players": players}

        detector = EventDetector({})
        events = detector.detect_all_events(frame0, frame1)
        moves = _events_of_type(events, EventType.MOVE)
        assert len(moves) == 0

    def test_multiple_simultaneous_moves(self):
        """TC-E3: 3 players change zones simultaneously → 3 MOVE events."""
        p0 = [
            {"track_id": "t1", "zone": "z7", "jersey_number": None, "team": "white"},
            {"track_id": "t2", "zone": "z8", "jersey_number": None, "team": "white"},
            {"track_id": "t3", "zone": "z9", "jersey_number": None, "team": "white"},
        ]
        p1 = [
            {"track_id": "t1", "zone": "z6", "jersey_number": None, "team": "white"},
            {"track_id": "t2", "zone": "z7", "jersey_number": None, "team": "white"},
            {"track_id": "t3", "zone": "z10", "jersey_number": None, "team": "white"},
        ]
        frame0 = {"timestamp": "0.0", "ball": {"holder_track_id": "t1", "zone": "z7", "state": "Holding"}, "players": p0}
        frame1 = {"timestamp": "0.5", "ball": {"holder_track_id": "t1", "zone": "z6", "state": "Holding"}, "players": p1}

        detector = EventDetector({})
        events = detector.detect_all_events(frame0, frame1)
        moves = _events_of_type(events, EventType.MOVE)
        assert len(moves) == 3
