"""
Role assignment module for Stage 2 inference.

Assigns player roles based on:
- Zone positions with relative L→R ordering for backs
- Wing-to-Pivot transitions
- Jersey continuity for persistence

14-Zone Court Layout (from gemini_context_zones.md):
  z0:  Goal area (center)
  z1:  Right wing corner (display RIGHT, x~18.5m)
  z2:  Right-center 6-8m (x~15.5m)
  z3:  Center 6-8m (x~10m)
  z4:  Left-center 6-8m (x~4.5m)
  z5:  Left wing corner (display LEFT, x~1.5m)
  z6:  Far left back (display LEFT, x~1.5m)
  z7:  Left-center back (x~5m)
  z8:  Center back (x~10m)
  z9:  Right-center back (x~15m)
  z10: Far right back (display RIGHT, x~18.5m)
  z11: Deep right (display RIGHT, x~16.5m)
  z12: Deep center (x~10m)
  z13: Deep left (display LEFT, x~3.5m)

Display convention: LEFT=x small, RIGHT=x large (attacker's perspective facing goal).
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


# Zone layout (0-13)
# 0: Goal
# 1-5: 6m-8m — Wings (z1=RW, z5=LW), Pivot (z2-z4)
# 6-10: 8m-10m (backcourt/9m line) — Back players
# 11-13: 10m+ (deep court)

# Wing zones (side positions)
LEFT_WING_ZONES = [5, 6]    # z5 = left wing corner, z6 = far left back
RIGHT_WING_ZONES = [1, 10]  # z1 = right wing corner, z10 = far right back

# Pivot zones (center-ish, between 6m and 9m)
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
    """Convert zone to approximate x-position (0=left, 1=right on display).

    Matches the 14-zone court layout:
      6m-8m band: z5(left)=0.0 → z1(right)=1.0
      8m-10m band: z6(left)=0.0 → z10(right)=1.0
      Deep band: z13(left)=0.17 → z11(right)=0.83
    """
    zone_x = {
        0: 0.5,   # Goal - center
        5: 0.0, 4: 0.2, 3: 0.5, 2: 0.8, 1: 1.0,  # 6m-8m (z5=left to z1=right)
        6: 0.0, 7: 0.25, 8: 0.5, 9: 0.75, 10: 1.0,  # 8m-10m
        13: 0.17, 12: 0.5, 11: 0.83,  # Deep (z13=left to z11=right)
    }
    return zone_x.get(zone, 0.5)


def is_left_side(zone: int) -> bool:
    """Check if zone is on left side of court (display left)."""
    return zone in [5, 4, 6, 7, 13]


def is_right_side(zone: int) -> bool:
    """Check if zone is on right side of court (display right)."""
    return zone in [1, 2, 9, 10, 11]


def is_center(zone: int) -> bool:
    """Check if zone is in center of court."""
    return zone in [3, 8, 12]


def assign_attack_roles(players: List[PlayerPosition]) -> Dict[str, str]:
    """
    Assign attacking roles based on player positions.
    Uses zone position to assign wings, pivot, and backs.

    Returns: Dictionary mapping track_id to role (no duplicates).
    """
    if not players:
        return {}

    roles = {}
    assigned = set()

    # Sort players by x position for consistent ordering
    sorted_players = sorted(players, key=lambda p: zone_to_x_position(p.zone))

    # 1. Left Wing: leftmost player in left wing zones
    for p in sorted_players:
        if p.zone in LEFT_WING_ZONES and p.track_id not in assigned:
            roles[p.track_id] = "LW"
            assigned.add(p.track_id)
            break

    # 2. Right Wing: rightmost player in right wing zones
    for p in reversed(sorted_players):
        if p.zone in RIGHT_WING_ZONES and p.track_id not in assigned:
            roles[p.track_id] = "RW"
            assigned.add(p.track_id)
            break

    # 3. Pivot: first unassigned player in pivot zones (center 6-8m)
    for p in sorted_players:
        if p.zone in PIVOT_ZONES and p.track_id not in assigned:
            roles[p.track_id] = "PV"
            assigned.add(p.track_id)
            break

    # 4. Back players: remaining unassigned in back zones, sorted L→R
    backs = [p for p in sorted_players if p.zone in BACK_ZONES and p.track_id not in assigned]
    back_roles = assign_back_roles_by_order(backs)
    for tid, role in back_roles.items():
        roles[tid] = role
        assigned.add(tid)

    # 5. Any remaining unassigned players
    for p in players:
        if p.track_id not in assigned:
            roles[p.track_id] = "UNK"

    return roles


def assign_back_roles_by_order(backs: List[PlayerPosition]) -> Dict[str, str]:
    """
    Assign LB, CB, RB based on relative left-to-right position.

    The relative ordering determines roles, not absolute zones.
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

    role_weights = weights.get(
        candidate_role,
        {"jersey": 0.25, "zone": 0.25, "order": 0.25, "distance": 0.25},
    )

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
