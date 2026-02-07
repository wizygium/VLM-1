"""
Role assignment module for Stage 2 inference.

Assigns player roles based on:
- Zone positions with relative L→R ordering for backs
- Wing-to-Pivot transitions
- Jersey continuity for persistence
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


# Zone layout (0-13)
# 0: Goal
# 1-5: 6m-8m (close to goal) - Wings and PV zone
# 6-10: 8m-10m (backcourt/9m line) - Back players
# 11-13: 10m+ (deep court)

# Wing zones (side positions)
LEFT_WING_ZONES = [1, 2, 6]
RIGHT_WING_ZONES = [5, 4, 10]

# Pivot zones (center, between 6m and 9m)
PIVOT_ZONES = [2, 3, 4]

# Back court zones
BACK_ZONES = [6, 7, 8, 9, 10]

# Defense roles (left to right)
DEFENSE_ROLES = ["DL1", "DL2", "DL3", "DR3", "DR2", "DR1"]


@dataclass
class PlayerPosition:
    track_id: str
    zone: int
    jersey_number: Optional[str] = None
    prev_role: Optional[str] = None  # For role transition tracking


def zone_to_x_position(zone: int) -> float:
    """Convert zone to approximate x-position (0=left, 1=right)."""
    zone_x = {
        0: 0.5,   # Goal - center
        1: 0.0, 2: 0.2, 3: 0.5, 4: 0.8, 5: 1.0,  # 6m-8m
        6: 0.0, 7: 0.25, 8: 0.5, 9: 0.75, 10: 1.0,  # 8m-10m
        11: 0.17, 12: 0.5, 13: 0.83,  # Deep
    }
    return zone_x.get(zone, 0.5)


def is_left_side(zone: int) -> bool:
    """Check if zone is on left side of court."""
    return zone in [1, 2, 6, 7, 11]


def is_right_side(zone: int) -> bool:
    """Check if zone is on right side of court."""
    return zone in [4, 5, 9, 10, 13]


def is_center(zone: int) -> bool:
    """Check if zone is in center of court."""
    return zone in [3, 8, 12]


def assign_attack_roles(players: List[PlayerPosition]) -> Dict[str, str]:
    """
    Assign attacking roles based on player positions.
    Uses relative left-to-right ordering for back players.
    
    Returns: Dictionary mapping track_id to role
    """
    if not players:
        return {}
    
    roles = {}
    wings_assigned = {"LW": None, "RW": None}
    pivot_candidate = None
    backs = []
    
    # First pass: identify wings and pivot candidates
    for player in players:
        x_pos = zone_to_x_position(player.zone)
        
        # Left wing: leftmost in wing zones
        if player.zone in LEFT_WING_ZONES and x_pos < 0.3:
            if wings_assigned["LW"] is None or x_pos < zone_to_x_position(players[wings_assigned["LW"]].zone if isinstance(wings_assigned["LW"], int) else 0):
                wings_assigned["LW"] = player.track_id
                roles[player.track_id] = "LW"
                continue
        
        # Right wing: rightmost in wing zones
        if player.zone in RIGHT_WING_ZONES and x_pos > 0.7:
            if wings_assigned["RW"] is None:
                wings_assigned["RW"] = player.track_id
                roles[player.track_id] = "RW"
                continue
        
        # Pivot: center zones 2-4, between 6m-9m
        if player.zone in PIVOT_ZONES and pivot_candidate is None:
            pivot_candidate = player.track_id
            continue
        
        # Otherwise, consider as back player
        if player.zone in BACK_ZONES:
            backs.append(player)
    
    # Assign pivot if found
    if pivot_candidate and pivot_candidate not in roles:
        roles[pivot_candidate] = "PV"
    
    # Assign back roles by relative L→R ordering
    back_roles = assign_back_roles_by_order(backs)
    roles.update(back_roles)
    
    return roles


def assign_back_roles_by_order(backs: List[PlayerPosition]) -> Dict[str, str]:
    """
    Assign LB, CB, RB based on relative left-to-right position.
    
    The relative ordering determines roles, not absolute zones.
    If CB moves right of RB position but RB is still rightmost,
    RB stays RB.
    """
    if not backs:
        return {}
    
    # Sort by x position (left to right)
    sorted_backs = sorted(backs, key=lambda p: zone_to_x_position(p.zone))
    
    role_names = ["LB", "CB", "RB"]
    roles = {}
    
    for i, player in enumerate(sorted_backs[:3]):
        if i < len(role_names):
            roles[player.track_id] = role_names[i]
    
    return roles


def detect_role_transition(
    player: PlayerPosition,
    prev_role: str
) -> Tuple[str, Optional[str]]:
    """
    Detect role transitions (e.g., wing → 2nd pivot, back → 2nd pivot).
    
    Returns: (new_role, transition_type or None)
    """
    # Wing to 2nd Pivot: wing moves to center zones
    if prev_role in ["LW", "RW"]:
        if player.zone in PIVOT_ZONES:
            return "2PV", "WING_TO_PIVOT"
    
    # Back to 2nd Pivot: back moves forward into pivot zones
    if prev_role in ["LB", "CB", "RB"]:
        if player.zone in PIVOT_ZONES:
            return "2PV", "BACK_TO_PIVOT"
    
    # 2nd Pivot back to Wing: returns to side zones
    if prev_role == "2PV":
        if player.zone in LEFT_WING_ZONES:
            return "LW", "PIVOT_TO_WING"
        if player.zone in RIGHT_WING_ZONES:
            return "RW", "PIVOT_TO_WING"
        # 2PV returning to backcourt becomes CB (default)
        if player.zone in BACK_ZONES:
            return "CB", "PIVOT_TO_BACK"
    
    return prev_role, None


def assign_defense_roles(players: List[PlayerPosition]) -> Dict[str, str]:
    """
    Assign defensive roles based on left-to-right ordering.
    DL1, DL2, DL3, DR3, DR2, DR1
    """
    if not players:
        return {}
    
    sorted_players = sorted(players, key=lambda p: zone_to_x_position(p.zone))
    
    roles = {}
    for i, player in enumerate(sorted_players):
        if i < len(DEFENSE_ROLES):
            roles[player.track_id] = DEFENSE_ROLES[i]
    
    return roles


def compute_role_weight(
    player: PlayerPosition,
    candidate_role: str,
    prev_role: Optional[str],
    prev_jersey: Optional[str]
) -> float:
    """
    Compute confidence weight for role assignment.
    Uses per-role weights as defined in inference plan.
    """
    weights = {
        "LW": {"jersey": 0.5, "zone": 0.2, "order": 0.1, "distance": 0.2},
        "RW": {"jersey": 0.5, "zone": 0.2, "order": 0.1, "distance": 0.2},
        "PV": {"jersey": 0.4, "zone": 0.3, "order": 0.1, "distance": 0.2},
        "LB": {"jersey": 0.4, "zone": 0.2, "order": 0.3, "distance": 0.1},
        "CB": {"jersey": 0.4, "zone": 0.2, "order": 0.3, "distance": 0.1},
        "RB": {"jersey": 0.4, "zone": 0.2, "order": 0.3, "distance": 0.1},
    }
    
    role_weights = weights.get(candidate_role, {"jersey": 0.25, "zone": 0.25, "order": 0.25, "distance": 0.25})
    
    score = 0.0
    
    # Jersey continuity (high weight)
    if prev_jersey and player.jersey_number == prev_jersey:
        score += role_weights["jersey"]
    
    # Zone match
    typical_zones = {
        "LW": LEFT_WING_ZONES,
        "RW": RIGHT_WING_ZONES,
        "PV": PIVOT_ZONES,
        "LB": [6, 7],
        "CB": [7, 8, 9],
        "RB": [9, 10],
    }
    if candidate_role in typical_zones and player.zone in typical_zones[candidate_role]:
        score += role_weights["zone"]
    
    # Role continuity
    if prev_role == candidate_role:
        score += role_weights["order"]
    
    return score


def track_roles_across_frames(
    prev_roles: Dict[str, str],
    prev_jerseys: Dict[str, str],
    current_positions: List[PlayerPosition]
) -> Dict[str, str]:
    """
    Update role assignments across frames using jersey continuity
    and role transition detection.
    """
    if not prev_roles:
        return assign_attack_roles(current_positions)
    
    current_ids = {p.track_id for p in current_positions}
    new_roles = {}
    
    for player in current_positions:
        if player.track_id in prev_roles:
            prev_role = prev_roles[player.track_id]
            # Check for role transition
            new_role, _ = detect_role_transition(player, prev_role)
            new_roles[player.track_id] = new_role
        else:
            # New player - assign based on position
            new_roles[player.track_id] = "UNK"
    
    return new_roles
