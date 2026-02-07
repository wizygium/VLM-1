"""
Event detection module for Stage 2 inference.

Derives events (PASS, SHOT, MOVE, TURNOVER) by comparing consecutive physics frames.
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
    turnover_type: Optional[str] = None  # For TURNOVER: STEAL, OUT_OF_BOUNDS, FOUL
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "event_id": self.event_id,
            "type": self.type.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
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
                "to_track_id": self.to_track_id,  # Defender who stole (if STEAL)
            })
        
        return result


class EventDetector:
    """Detects events by comparing consecutive physics frames."""
    
    def __init__(self, roles: Dict[str, str], attacker_ids: Set[str] = None, defender_ids: Set[str] = None):
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
    
    def detect_pass(self, frame_n: Dict, frame_n1: Dict) -> Optional[Event]:
        """
        Detect PASS event when ball holder changes.
        
        Simplified: If holder changes between attackers, a pass occurred
        (even without explicit In-Air detection).
        """
        ball_n = frame_n.get("ball", {})
        ball_n1 = frame_n1.get("ball", {})
        
        holder_n = ball_n.get("holder_track_id")
        holder_n1 = ball_n1.get("holder_track_id")
        
        # Ball changed hands between two valid holders
        if holder_n != holder_n1 and holder_n is not None and holder_n1 is not None:
            # Both are attackers = PASS
            if self._is_attacker(holder_n) and self._is_attacker(holder_n1):
                return Event(
                    event_id=self._next_event_id(),
                    type=EventType.PASS,
                    start_time=frame_n.get("timestamp", 0),
                    end_time=frame_n1.get("timestamp", 0),
                    from_track_id=holder_n,
                    from_role=self.roles.get(holder_n),
                    from_zone=ball_n.get("zone"),
                    to_track_id=holder_n1,
                    to_role=self.roles.get(holder_n1),
                    to_zone=ball_n1.get("zone"),
                )
        
        return None
    
    def detect_shot(self, frame_n: Dict, frame_n1: Dict, is_last_frame: bool = False) -> Optional[Event]:
        """
        Detect SHOT event when ball enters goal zone (0).
        
        Note: Shots typically only occur at scene end.
        """
        ball_n = frame_n.get("ball", {})
        ball_n1 = frame_n1.get("ball", {})
        
        zone_n = self._normalize_zone(ball_n.get("zone"))
        zone_n1 = self._normalize_zone(ball_n1.get("zone"))
        holder_n = ball_n.get("holder_track_id")
        
        # Ball trajectory towards goal
        if zone_n != 0 and zone_n1 == 0:
            state_n1 = ball_n1.get("state", "").lower()
            outcome = "ON_TARGET"
            if "goal" in state_n1 or "net" in state_n1:
                outcome = "GOAL"
            elif "save" in state_n1 or "block" in state_n1:
                outcome = "SAVE"
            
            return Event(
                event_id=self._next_event_id(),
                type=EventType.SHOT,
                start_time=frame_n.get("timestamp", 0),
                end_time=frame_n1.get("timestamp", 0),
                from_track_id=holder_n,
                from_role=self.roles.get(holder_n) if holder_n else None,
                from_zone=zone_n,
                outcome=outcome,
            )
        
        return None
    
    def detect_turnover(self, frame_n: Dict, frame_n1: Dict) -> Optional[Event]:
        """
        Detect TURNOVER: loss of possession.
        
        Types:
        - STEAL: Defender takes ball from attacker
        - OUT_OF_BOUNDS: Ball goes over sideline (state = "Out")
        - FOUL: Attacking foul (future: referee signal detection)
        """
        ball_n = frame_n.get("ball", {})
        ball_n1 = frame_n1.get("ball", {})
        
        holder_n = ball_n.get("holder_track_id")
        holder_n1 = ball_n1.get("holder_track_id")
        state_n1 = ball_n1.get("state", "")
        
        # Out of bounds detection
        if state_n1.lower() in ["out", "out_of_bounds", "sideline"]:
            return Event(
                event_id=self._next_event_id(),
                type=EventType.TURNOVER,
                start_time=frame_n.get("timestamp", 0),
                end_time=frame_n1.get("timestamp", 0),
                from_track_id=holder_n,
                from_role=self.roles.get(holder_n) if holder_n else None,
                turnover_type="OUT_OF_BOUNDS",
            )
        
        # Steal detection: attacker had ball, now defender has it
        if self._is_attacker(holder_n) and self._is_defender(holder_n1):
            return Event(
                event_id=self._next_event_id(),
                type=EventType.TURNOVER,
                start_time=frame_n.get("timestamp", 0),
                end_time=frame_n1.get("timestamp", 0),
                from_track_id=holder_n,
                from_role=self.roles.get(holder_n),
                turnover_type="STEAL",
                to_track_id=holder_n1,
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
    
    def _normalize_zone(self, zone: Any) -> int:
        """Convert zone to integer format."""
        if isinstance(zone, int):
            return zone
        if isinstance(zone, str):
            return int(zone.replace("z", ""))
        return 0
    
    def detect_all_events(self, frame_n: Dict, frame_n1: Dict, is_last_frame: bool = False) -> List[Event]:
        """Detect all event types between two frames."""
        events = []
        
        # Check for turnover first (takes precedence)
        turnover = self.detect_turnover(frame_n, frame_n1)
        if turnover:
            events.append(turnover)
            return events  # Turnover ends the play
        
        # Check for pass
        pass_event = self.detect_pass(frame_n, frame_n1)
        if pass_event:
            events.append(pass_event)
        
        # Check for shot
        shot_event = self.detect_shot(frame_n, frame_n1, is_last_frame)
        if shot_event:
            events.append(shot_event)
        
        # Check for moves
        move_events = self.detect_moves(frame_n, frame_n1)
        events.extend(move_events)
        
        return events
