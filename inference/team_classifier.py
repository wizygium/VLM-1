"""
Team classification module for Stage 2 inference.

Determines which team colour is attacking vs defending by scoring multiple
independent physical signals from the physics frames.

Signals:
  1. Ball possession (weight 0.45) — team holding the ball most = attacking
  2. GK spatial confirmation (weight 0.25) — team nearest to z0 GK = defending
  3. Average zone depth (weight 0.20) — deeper avg zone = attacking
  4. Defensive formation (weight 0.10) — high proportion in z1-z5 = defending

If no GK is detected, Signal 2 weight is redistributed to other signals.
If team labels are already "attack"/"defense", those are used directly.

See: https://github.com/wizygium/VLM-1/issues/32
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Tuple
from collections import defaultdict


@dataclass
class TeamClassification:
    """Result of team classification."""

    attacking_team: str
    defending_team: str
    goalkeeper_team: Optional[str] = None
    confidence: float = 0.0
    signals: Dict[str, Any] = field(default_factory=dict)


# Approximate depth in metres from goal for each zone band.
ZONE_DEPTH_METRES = {
    0: 0.0,   # Goal
    1: 7.0, 2: 7.0, 3: 7.0, 4: 7.0, 5: 7.0,          # 6m–8m
    6: 9.0, 7: 9.0, 8: 9.0, 9: 9.0, 10: 9.0,           # 8m–10m
    11: 11.0, 12: 11.0, 13: 11.0,                        # 10m+
}


def _normalize_zone(zone) -> int:
    """Convert zone to integer."""
    if isinstance(zone, int):
        return zone
    if isinstance(zone, str):
        return int(zone.replace("z", ""))
    return 0


# ---------------------------------------------------------------------------
# Internal: identify field teams vs goalkeeper
# ---------------------------------------------------------------------------


def _get_field_teams_and_gk(
    frames: List[Dict],
) -> Tuple[Set[str], Optional[str]]:
    """Identify field teams and goalkeeper colour.

    The goalkeeper wears a unique colour and is predominantly in z0.
    Returns (field_teams, goalkeeper_team_or_None).
    """
    # Track zone appearances per team across ALL frames
    team_zone_counts: Dict[str, Dict[int, int]] = defaultdict(lambda: defaultdict(int))

    for frame in frames:
        for p in frame.get("players", []):
            team = p.get("team")
            if not team:
                continue
            zone = _normalize_zone(p.get("zone", 0))
            team_zone_counts[team][zone] += 1

    if not team_zone_counts:
        return set(), None

    # A team is a GK candidate if ≥80 % of its appearances are in z0
    # AND it is not the only team (need at least 2 field teams).
    gk_team: Optional[str] = None
    field_teams: Set[str] = set()

    for team, zone_counts in team_zone_counts.items():
        total = sum(zone_counts.values())
        z0_count = zone_counts.get(0, 0)
        z0_ratio = z0_count / total if total > 0 else 0

        if z0_ratio >= 0.8:
            if gk_team is None:
                gk_team = team
            else:
                # Multiple GK candidates → ambiguous, treat all as field teams
                field_teams.add(team)
                field_teams.add(gk_team)
                gk_team = None
                break
        else:
            field_teams.add(team)

    if gk_team:
        field_teams.discard(gk_team)

    # If no clear GK detected, every team is a field team
    if gk_team is None:
        field_teams = set(team_zone_counts.keys())

    return field_teams, gk_team


# ---------------------------------------------------------------------------
# Signal functions — each returns {team: score} where 0‑1, higher = more
# likely to be the ATTACKING team.
# ---------------------------------------------------------------------------


def _signal_possession(
    frames: List[Dict], field_teams: Set[str]
) -> Dict[str, float]:
    """Signal 1: Ball possession ratio per field team (0–1)."""
    possession_count: Dict[str, int] = defaultdict(int)
    total_held = 0

    for frame in frames:
        ball = frame.get("ball", {})
        holder_id = ball.get("holder_track_id")
        if not holder_id:
            continue
        # Find holder's team
        for p in frame.get("players", []):
            if p["track_id"] == holder_id:
                team = p.get("team")
                if team and team in field_teams:
                    possession_count[team] += 1
                    total_held += 1
                break

    if total_held == 0:
        # No holders → signal inconclusive
        return {t: 0.0 for t in field_teams}

    return {t: possession_count[t] / total_held for t in field_teams}


def _signal_gk_spatial(
    frames: List[Dict],
    field_teams: Set[str],
    gk_team: Optional[str],
) -> Dict[str, float]:
    """Signal 2: GK spatial proximity.

    The field team with a HIGHER proportion of players in z1–z5 (near the
    defended goal) is more likely defending.
    Returns attack score: 1 = far from GK (attacking), 0 = near GK (defending).
    Returns empty dict when no GK is detected (signal inactive).
    """
    if not gk_team:
        return {}

    near_goal: Dict[str, int] = defaultdict(int)
    total: Dict[str, int] = defaultdict(int)

    for frame in frames:
        for p in frame.get("players", []):
            team = p.get("team")
            if team not in field_teams:
                continue
            zone = _normalize_zone(p.get("zone", 0))
            if zone == 0:
                continue  # Exclude GK zone from field stats
            total[team] += 1
            if 1 <= zone <= 5:
                near_goal[team] += 1

    ratios: Dict[str, float] = {}
    for team in field_teams:
        if total[team] > 0:
            ratios[team] = near_goal[team] / total[team]
        else:
            ratios[team] = 0.0

    if not ratios:
        return {}

    min_r = min(ratios.values())
    max_r = max(ratios.values())
    if max_r == min_r:
        return {t: 0.5 for t in field_teams}

    # Lower near-goal ratio → higher attack score (further from GK)
    return {
        t: 1.0 - (ratios[t] - min_r) / (max_r - min_r)
        for t in field_teams
    }


def _signal_zone_depth(
    frames: List[Dict], field_teams: Set[str]
) -> Dict[str, float]:
    """Signal 3: Average zone depth (metres from goal).

    Higher average depth → more likely attacking (backcourt).
    Returns attack score normalised 0–1 between the two teams.
    """
    depth_sums: Dict[str, float] = defaultdict(float)
    depth_counts: Dict[str, int] = defaultdict(int)

    for frame in frames:
        for p in frame.get("players", []):
            team = p.get("team")
            if team not in field_teams:
                continue
            zone = _normalize_zone(p.get("zone", 0))
            if zone == 0:
                continue
            depth = ZONE_DEPTH_METRES.get(zone, 7.0)
            depth_sums[team] += depth
            depth_counts[team] += 1

    avg_depths: Dict[str, float] = {}
    for team in field_teams:
        if depth_counts[team] > 0:
            avg_depths[team] = depth_sums[team] / depth_counts[team]
        else:
            avg_depths[team] = 7.0  # Neutral midpoint

    min_d = min(avg_depths.values()) if avg_depths else 7.0
    max_d = max(avg_depths.values()) if avg_depths else 7.0
    if max_d == min_d:
        return {t: 0.5 for t in field_teams}

    return {
        t: (avg_depths[t] - min_d) / (max_d - min_d)
        for t in field_teams
    }


def _signal_formation(
    frames: List[Dict], field_teams: Set[str]
) -> Dict[str, float]:
    """Signal 4: Defensive formation detection.

    A high proportion of players in z1–z5 = defensive wall.
    Returns attack score: lower 6m‑ratio → higher score (more attacking).
    """
    in_6m: Dict[str, int] = defaultdict(int)
    total: Dict[str, int] = defaultdict(int)

    for frame in frames:
        for p in frame.get("players", []):
            team = p.get("team")
            if team not in field_teams:
                continue
            zone = _normalize_zone(p.get("zone", 0))
            if zone == 0:
                continue
            total[team] += 1
            if 1 <= zone <= 5:
                in_6m[team] += 1

    ratios: Dict[str, float] = {}
    for team in field_teams:
        if total[team] > 0:
            ratios[team] = in_6m[team] / total[team]
        else:
            ratios[team] = 0.5

    min_r = min(ratios.values()) if ratios else 0.5
    max_r = max(ratios.values()) if ratios else 0.5
    if max_r == min_r:
        return {t: 0.5 for t in field_teams}

    # Lower 6m ratio → higher attack score
    return {
        t: 1.0 - (ratios[t] - min_r) / (max_r - min_r)
        for t in field_teams
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def determine_attacking_team(frames: List[Dict]) -> TeamClassification:
    """Determine which team colour is attacking based on physical signals.

    Uses 4 independent signals with configurable weights to produce a robust
    determination that works regardless of jersey colour.

    If team labels are already ``"attack"``/``"defense"``, those are used
    directly (backward compatible).

    Returns:
        TeamClassification with attacking/defending teams and confidence.
    """
    if not frames:
        return TeamClassification(
            attacking_team="unknown",
            defending_team="unknown",
            confidence=0.0,
            signals={"error": "no frames"},
        )

    # --- Check for explicit labels (backward compat) ---
    all_teams: Set[str] = set()
    for frame in frames:
        for p in frame.get("players", []):
            t = p.get("team")
            if t:
                all_teams.add(t)

    if "attack" in all_teams and "defense" in all_teams:
        return TeamClassification(
            attacking_team="attack",
            defending_team="defense",
            confidence=1.0,
            signals={"explicit_labels": True},
        )

    # --- Identify field teams and goalkeeper ---
    field_teams, gk_team = _get_field_teams_and_gk(frames)

    if len(field_teams) < 2:
        # Can't classify with fewer than 2 field teams — best-effort
        team_list = sorted(field_teams)
        return TeamClassification(
            attacking_team=team_list[0] if team_list else "unknown",
            defending_team="unknown",
            goalkeeper_team=gk_team,
            confidence=0.0,
            signals={
                "error": "fewer than 2 field teams",
                "field_teams": team_list,
            },
        )

    # --- Compute signals ---
    sig_possession = _signal_possession(frames, field_teams)
    sig_gk = _signal_gk_spatial(frames, field_teams, gk_team)
    sig_depth = _signal_zone_depth(frames, field_teams)
    sig_formation = _signal_formation(frames, field_teams)

    # --- Weighted scoring ---
    # When GK is detected, use all 4 signals.
    # When no GK, redistribute Signal 2 weight to the others.
    if sig_gk:
        w_poss, w_gk, w_depth, w_form = 0.45, 0.25, 0.20, 0.10
    else:
        # Without GK, possession must be strong enough to override
        # depth + formation combined (0.55 > 0.25 + 0.20 = 0.45).
        w_poss, w_gk, w_depth, w_form = 0.55, 0.0, 0.25, 0.20

    scores: Dict[str, float] = {}
    for team in field_teams:
        s = 0.0
        s += w_poss * sig_possession.get(team, 0.0)
        s += w_gk * sig_gk.get(team, 0.5)
        s += w_depth * sig_depth.get(team, 0.5)
        s += w_form * sig_formation.get(team, 0.5)
        scores[team] = s

    # --- Select attacking team (highest score) ---
    sorted_teams = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    attacking = sorted_teams[0][0]
    defending = sorted_teams[1][0]

    # Confidence = difference between top two scores normalised to 0–1
    max_possible = w_poss + w_gk + w_depth + w_form  # = 1.0
    score_diff = sorted_teams[0][1] - sorted_teams[1][1]
    confidence = min(score_diff / max_possible, 1.0) if max_possible > 0 else 0.0

    return TeamClassification(
        attacking_team=attacking,
        defending_team=defending,
        goalkeeper_team=gk_team,
        confidence=confidence,
        signals={
            "possession": dict(sig_possession),
            "gk_spatial": dict(sig_gk) if sig_gk else None,
            "zone_depth": dict(sig_depth),
            "formation": dict(sig_formation),
            "scores": dict(scores),
            "weights": {
                "possession": w_poss,
                "gk_spatial": w_gk,
                "depth": w_depth,
                "formation": w_form,
            },
        },
    )
