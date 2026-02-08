"""Inference modules for Stage 2 programmatic event derivation."""

from .role_assigner import (
    assign_attack_roles,
    assign_defense_roles,
    track_roles_across_frames,
    PlayerPosition,
)
from .event_detector import EventDetector, Event, EventType
from .team_classifier import determine_attacking_team, TeamClassification

__all__ = [
    "assign_attack_roles",
    "assign_defense_roles",
    "track_roles_across_frames",
    "PlayerPosition",
    "EventDetector",
    "Event",
    "EventType",
    "determine_attacking_team",
    "TeamClassification",
]
