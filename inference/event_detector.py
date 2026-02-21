"""
Event detection module for Stage 2 inference.

Derives events (PASS, SHOT, MOVE, TURNOVER) by comparing consecutive physics frames.

Uses a state machine to track ball possession across In-Air frames, enabling
detection of passes that span multiple frames (Holding→In-Air→...→Holding).
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Set
from enum import Enum


class EventType(Enum):
    PASS = "PASS"
    SHOT = "SHOT"
    GOAL = "GOAL"
    SAVE = "SAVE"
    MOVE = "MOVE"
    DRIBBLE = "DRIBBLE"
    TURNOVER = "TURNOVER"


@dataclass
class Event:
    event_id: int
    type: EventType
    start_time: float
    end_time: float
    from_track_id: Optional[str] = None
    from_role: Optional[str] = None
    from_zone: Optional[int] = None
    to_track_id: Optional[str] = None
    to_role: Optional[str] = None
    to_zone: Optional[int] = None
    track_id: Optional[str] = None  # For MOVE events
    role: Optional[str] = None  # For MOVE events
    outcome: Optional[str] = None  # For SHOT events
    turnover_type: Optional[str] = None  # For TURNOVER: STEAL, OUT_OF_BOUNDS, LOST_BALL

    @property
    def action_time(self) -> float:
        """Estimated moment the action occurs — midpoint of the bounding frames."""
        return (float(self.start_time) + float(self.end_time)) / 2

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "event_id": self.event_id,
            "type": self.type.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "action_time": self.action_time,
        }

        if self.type == EventType.PASS:
            result.update({
                "from_track_id": self.from_track_id,
                "from_role": self.from_role,
                "from_zone": self.from_zone,
                "to_track_id": self.to_track_id,
                "to_role": self.to_role,
                "to_zone": self.to_zone,
            })
        elif self.type in [EventType.SHOT, EventType.GOAL, EventType.SAVE]:
            result.update({
                "from_track_id": self.from_track_id,
                "from_role": self.from_role,
                "from_zone": self.from_zone,
                "outcome": self.outcome,
            })
        elif self.type == EventType.MOVE:
            result.update({
                "track_id": self.track_id,
                "role": self.role,
                "from_zone": self.from_zone,
                "to_zone": self.to_zone,
            })
        elif self.type == EventType.TURNOVER:
            result.update({
                "from_track_id": self.from_track_id,
                "from_role": self.from_role,
                "turnover_type": self.turnover_type,
                "to_track_id": self.to_track_id,
            })

        return result


class EventDetector:
    """Detects events by comparing consecutive physics frames.

    Maintains internal state (last known ball holder) across calls to
    detect_all_events() so that passes spanning In-Air frames are captured.
    """

    def __init__(
        self,
        roles: Dict[str, str],
        attacker_ids: Set[str] = None,
        defender_ids: Set[str] = None,
    ):
        """
        Args:
            roles: Dictionary mapping track_id to role
            attacker_ids: Set of track_ids that are attackers
            defender_ids: Set of track_ids that are defenders
        """
        self.roles = roles
        self.attacker_ids = attacker_ids or set()
        self.defender_ids = defender_ids or set()
        self.event_counter = 0

        # State machine: track last known ball holder across frames
        self._last_holder: Optional[str] = None
        self._last_holder_zone: Optional[int] = None
        self._last_holder_time: Optional[float] = None

    def _next_event_id(self) -> int:
        self.event_counter += 1
        return self.event_counter

    def _is_attacker(self, track_id: Optional[str]) -> bool:
        if not track_id:
            return False
        return track_id in self.attacker_ids

    def _is_defender(self, track_id: Optional[str]) -> bool:
        if not track_id:
            return False
        return track_id in self.defender_ids

    def _different_team(self, id_a: Optional[str], id_b: Optional[str]) -> bool:
        """Check if two track_ids are on KNOWN different teams.

        Returns True only when we can confirm they are on opposing teams.
        Returns False if either player's team is unknown.
        """
        if not id_a or not id_b:
            return False
        a_attack = id_a in self.attacker_ids
        a_defense = id_a in self.defender_ids
        b_attack = id_b in self.attacker_ids
        b_defense = id_b in self.defender_ids
        return (a_attack and b_defense) or (a_defense and b_attack)

    def _normalize_zone(self, zone: Any) -> int:
        """Convert zone to integer format."""
        if isinstance(zone, int):
            return zone
        if isinstance(zone, str):
            return int(zone.replace("z", ""))
        return 0

    def detect_shot(self, frame_n: Dict, frame_n1: Dict) -> Optional[Event]:
        """
        Detect SHOT event when ball enters goal zone (z0).
        """
        ball_n = frame_n.get("ball", {})
        ball_n1 = frame_n1.get("ball", {})

        zone_n = self._normalize_zone(ball_n.get("zone"))
        zone_n1 = self._normalize_zone(ball_n1.get("zone"))

        # Ball trajectory towards goal
        if zone_n != 0 and zone_n1 == 0:
            state_n1 = ball_n1.get("state", "").lower()
            outcome = "ON_TARGET"
            if "goal" in state_n1 or "net" in state_n1:
                outcome = "GOAL"
            elif "save" in state_n1 or "block" in state_n1:
                outcome = "SAVE"

            # Use last known holder as the shooter
            shooter = self._last_holder
            shooter_zone = self._last_holder_zone if self._last_holder_zone else zone_n

            return Event(
                event_id=self._next_event_id(),
                type=EventType.SHOT,
                start_time=self._last_holder_time or frame_n.get("timestamp", 0),
                end_time=frame_n1.get("timestamp", 0),
                from_track_id=shooter,
                from_role=self.roles.get(shooter) if shooter else None,
                from_zone=shooter_zone,
                outcome=outcome,
            )

        return None

    def detect_moves(self, frame_n: Dict, frame_n1: Dict) -> List[Event]:
        """
        Detect MOVE events when player zones change.
        Requires consistent track_id between frames.
        """
        events = []

        players_n = {p["track_id"]: p for p in frame_n.get("players", [])}
        players_n1 = {p["track_id"]: p for p in frame_n1.get("players", [])}

        for track_id, player_n in players_n.items():
            if track_id in players_n1:
                player_n1 = players_n1[track_id]
                zone_n = self._normalize_zone(player_n.get("zone"))
                zone_n1 = self._normalize_zone(player_n1.get("zone"))

                if zone_n != zone_n1:
                    events.append(Event(
                        event_id=self._next_event_id(),
                        type=EventType.MOVE,
                        start_time=frame_n.get("timestamp", 0),
                        end_time=frame_n1.get("timestamp", 0),
                        track_id=track_id,
                        role=self.roles.get(track_id),
                        from_zone=zone_n,
                        to_zone=zone_n1,
                    ))

        return events

    def detect_all_events(
        self, frame_n: Dict, frame_n1: Dict, is_last_frame: bool = False
    ) -> List[Event]:
        """Detect all event types between two consecutive frames.

        Uses internal state machine to track ball holder across In-Air frames.
        Must be called sequentially for each frame pair in order.
        """
        events = []

        ball_n = frame_n.get("ball", {})
        ball_n1 = frame_n1.get("ball", {})
        holder_n = ball_n.get("holder_track_id")
        holder_n1 = ball_n1.get("holder_track_id")
        state_n = ball_n.get("state", "")
        state_n1 = ball_n1.get("state", "")

        # --- Update state machine from frame_n ---
        if holder_n:
            self._last_holder = holder_n
            self._last_holder_zone = self._normalize_zone(ball_n.get("zone"))
            self._last_holder_time = frame_n.get("timestamp", 0)

        # --- 1. Out of bounds ---
        if state_n1.lower() in ["out", "out_of_bounds", "sideline"]:
            events.append(Event(
                event_id=self._next_event_id(),
                type=EventType.TURNOVER,
                start_time=self._last_holder_time or frame_n.get("timestamp", 0),
                end_time=frame_n1.get("timestamp", 0),
                from_track_id=self._last_holder,
                from_role=self.roles.get(self._last_holder) if self._last_holder else None,
                turnover_type="OUT_OF_BOUNDS",
            ))
            self._last_holder = None
            self._last_holder_zone = None
            self._last_holder_time = None
            return events

        # --- 2. Loose ball (possession lost) ---
        # Suppress when: (a) previous state was In-Air — ball just landed mid-pass,
        # or (b) ball entered goal zone z0 — that's a shot, not a turnover.
        zone_n1 = self._normalize_zone(ball_n1.get("zone"))
        if (
            state_n1.lower() == "loose"
            and state_n.lower() not in ("loose", "in-air")
            and zone_n1 != 0
        ):
            events.append(Event(
                event_id=self._next_event_id(),
                type=EventType.TURNOVER,
                start_time=self._last_holder_time or frame_n.get("timestamp", 0),
                end_time=frame_n1.get("timestamp", 0),
                from_track_id=self._last_holder,
                from_role=self.roles.get(self._last_holder) if self._last_holder else None,
                turnover_type="LOST_BALL",
            ))

        # --- 3. Shot into goal zone ---
        shot = self.detect_shot(frame_n, frame_n1)
        if shot:
            events.append(shot)

        # --- 4. Pass / Steal detection via state machine ---
        if holder_n1 and self._last_holder and holder_n1 != self._last_holder:
            # New holder is different from last known holder
            if self._different_team(self._last_holder, holder_n1):
                # Cross-team = STEAL / TURNOVER
                events.append(Event(
                    event_id=self._next_event_id(),
                    type=EventType.TURNOVER,
                    start_time=self._last_holder_time or frame_n.get("timestamp", 0),
                    end_time=frame_n1.get("timestamp", 0),
                    from_track_id=self._last_holder,
                    from_role=self.roles.get(self._last_holder),
                    turnover_type="STEAL",
                    to_track_id=holder_n1,
                ))
            else:
                # Same team or unknown team = PASS
                events.append(Event(
                    event_id=self._next_event_id(),
                    type=EventType.PASS,
                    start_time=self._last_holder_time or frame_n.get("timestamp", 0),
                    end_time=frame_n1.get("timestamp", 0),
                    from_track_id=self._last_holder,
                    from_role=self.roles.get(self._last_holder),
                    from_zone=self._last_holder_zone,
                    to_track_id=holder_n1,
                    to_role=self.roles.get(holder_n1),
                    to_zone=self._normalize_zone(ball_n1.get("zone")),
                ))

        # --- Update state machine from frame_n1 ---
        if holder_n1:
            self._last_holder = holder_n1
            self._last_holder_zone = self._normalize_zone(ball_n1.get("zone"))
            self._last_holder_time = frame_n1.get("timestamp", 0)

        # --- 5. Player movement ---
        move_events = self.detect_moves(frame_n, frame_n1)
        events.extend(move_events)

        return events
