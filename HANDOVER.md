# Handover Document: VLM-1 Handball Analysis Pipeline

**Date:** 2026-02-08
**Status:** Operational (Two-Stage Physics→Events Pipeline with automated team classification)

## 1. Project Overview

VLM-1 is a **Video Language Model (VLM) Pipeline** for analyzing handball match footage. It uses Gemini 3 Pro for video analysis and outputs structured JSON with spatial tracking and event detection.

**Key Innovations:**
- Two-stage pipeline separating physics observation (VLM) from event inference (Python)
- Multi-signal team classifier that infers attacking/defending teams from physical evidence (not hardcoded colours)
- 14-zone spatial system (z0-z13) with precise court geometry rendering
- Unified timeline UI showing raw physics frames alongside inferred events

## 2. Current Architecture

```
Stage 1: Physics Observation (Gemini VLM)
├── Input: Video file (MP4)
├── Output: *_physics.json
├── Content: Raw observations at 16fps
│   - Ball: holder_track_id, zone, state (Holding/In-Air/Loose)
│   - Players: track_id, zone, jersey_number, team colour
│   - NO role inference, NO event detection
└── Script: gemini_cache_analyzer_v2.py

Stage 2: Event Inference (Python)
├── Input: *_physics.json
├── Output: *_events.json
├── Content: Programmatic derivation
│   - Team classification (multi-signal: possession, GK, depth, formation)
│   - Roster with inferred roles (LW/RW/PV/LB/CB/RB, DL1-DR1)
│   - Events: PASS, SHOT, MOVE, TURNOVER with start_time/end_time
│   - Frames enriched with roles and active_event_ids
├── Modules:
│   - inference/team_classifier.py  — determines attacking/defending teams
│   - inference/event_detector.py   — state-machine pass/shot/turnover detection
│   - inference/role_assigner.py    — zone-based role assignment
└── Script: physics_to_events.py

Visualizer (Web UI)
├── Server: physics_visualizer/server.py (FastAPI, port 8001)
├── Frontend: physics_visualizer/static/ (HTML/JS/CSS)
│   - court-renderer.js: 14-zone system with polygonal rendering
│   - app.js: Unified timeline (physics frames + inferred events)
└── Features: video playback, court simulation, filterable timeline
```

### Why Two Stages?
- **Reduces Hallucination**: VLM only reports what it sees, doesn't guess events
- **100% Accurate Events**: Pass detection from physics state changes is deterministic
- **Cleaner UI**: Clear separation of raw state vs tactical interpretation

### Team Classification (Issue #32)
The VLM reports jersey **colours** (e.g., "white", "blue", "yellow"), not tactical roles. The team classifier infers which colour is attacking vs defending using 4 independent signals:

| Signal | Weight (GK) | Weight (no GK) | What it measures |
|--------|-------------|-----------------|------------------|
| Ball possession | 0.45 | 0.55 | Team holding ball most = attacking |
| GK spatial proximity | 0.25 | — | Team nearest to z0 goalkeeper = defending |
| Average zone depth | 0.20 | 0.25 | Deeper average zone = attacking (backcourt) |
| Defensive formation | 0.10 | 0.20 | High % of players in z1-z5 = defensive wall |

**Design decisions:**
- Possession weight is always highest — it alone should override other signals
- GK is detected as a unique colour predominantly in z0 (≥80% of appearances)
- Player count is NOT used (unreliable due to camera coverage, suspensions, 7v6 attacks)
- Explicit "attack"/"defense" labels are respected as overrides (backward compat)

## 3. Quick Start

### Prerequisites
```bash
export GEMINI_API_KEY=your-key-here
pip install -e ".[dev]"  # or: pip install google-genai click pytest
```

### Run Full Pipeline
```bash
# Stage 1: Physics (runs Gemini, ~3 mins per video)
python gemini_cache_analyzer_v2.py data/videos/clip.mp4 --output data/analyses --verbose

# Stage 2: Events (runs locally, instant)
python physics_to_events.py data/analyses/clip_physics.json -v
```

### Visualizer
```bash
cd physics_visualizer && python server.py
# Open http://127.0.0.1:8001
```

### Run Tests
```bash
pytest tests/ -v  # 59 tests covering team classifier, event detector, role assigner
```

## 4. Key Files

| File | Purpose |
|------|---------|
| `gemini_cache_analyzer_v2.py` | Stage 1: VLM physics extraction (16fps) |
| `physics_to_events.py` | Stage 2: Event inference from physics |
| `inference/team_classifier.py` | Multi-signal attacking/defending team determination |
| `inference/event_detector.py` | State-machine event detection (PASS, SHOT, TURNOVER, MOVE) |
| `inference/role_assigner.py` | Zone-based role assignment (LW/RW/PV/LB/CB/RB, DL1-DR1) |
| `prompts/physics_prompt.md` | VLM system instruction (14-zone, track-based) |
| `prompts/physics_prompt.md` | VLM system instruction (14-zone, track-based) |
| `physics_visualizer/` | Web UI: video + court simulation + timeline |
| `tests/` | Pytest suite (59 tests) |
| `data/videos/` | Input video directory |
| `data/analyses/` | Output JSON directory |
| `docs/` | Project documentation |
| `archive/` | Legacy scripts and results |

## 5. JSON Formats

### Physics JSON (Stage 1 output)
```json
{
  "metadata": {"video": "clip.mp4", "model": "gemini-3-pro-preview", "fps": 16.0},
  "frames": [
    {
      "timestamp": "1.000",
      "ball": {"holder_track_id": "t5", "zone": "z9", "state": "Holding"},
      "players": [
        {"track_id": "t5", "zone": "z9", "jersey_number": "23", "team": "blue"},
        {"track_id": "t1", "zone": "z3", "jersey_number": null, "team": "white"}
      ]
    }
  ]
}
```

### Events JSON (Stage 2 output)
```json
{
  "metadata": {
    "video": "clip.mp4",
    "team_classification": {
      "attacking_team": "white",
      "defending_team": "blue",
      "goalkeeper_team": "yellow",
      "confidence": 1.0
    }
  },
  "roster": {
    "attack": [{"track_id": "t5", "role": "CB", "jersey_number": "23"}],
    "defense": [{"track_id": "t1", "role": "DL1", "jersey_number": null}]
  },
  "events": [
    {"event_id": 1, "type": "PASS", "start_time": 1.0, "end_time": 1.5,
     "from_role": "CB", "to_role": "LB", "from_zone": 8, "to_zone": 7}
  ],
  "frames": [/* enriched frames with roles and active_event_ids */]
}
```

## 6. 14-Zone Court System

```
                        GOAL (z0)
    ┌─────────────────────────────────────────────┐
    │  z1 (LW)  z2 (LC)  z3 (C)  z4 (RC)  z5 (RW) │  6m–8m band
    ├─────────────────────────────────────────────┤
    │  z6 (LB)  z7 (LCB) z8 (CB) z9 (RCB) z10(RB) │  8m–10m band
    ├─────────────────────────────────────────────┤
    │      z11 (DL)    z12 (DC)    z13 (DR)         │  10m+ deep
    └─────────────────────────────────────────────┘
```

Zone numbering is from the **attacker's perspective facing goal**: z1 = far left, z5 = far right (matching `prompts/physics_prompt.md`).

## 7. Inference Module Design

### Event Detector (State Machine)
The `EventDetector` maintains `_last_holder` across frame pairs to handle In-Air sequences:
- `Holding(A) → In-Air → ... → Holding(B)` → PASS from A to B
- `Holding(A) → In-Air → Loose` → TURNOVER (LOST_BALL)
- `Holding(A) → Holding(B)` where A and B on different teams → TURNOVER (STEAL)
- Ball enters z0 → SHOT (outcome: ON_TARGET, GOAL, SAVE)

### Role Assigner
Assigns roles from zone positions in the first frame:
- Wings: z1/z6 → LW, z5/z10 → RW
- Pivot: z2/z3/z4 → PV
- Backs: z6-z10 sorted L→R → LB, CB, RB
- Defence: sorted L→R → DL1, DL2, DL3, DR3, DR2, DR1

**Note:** `role_assigner.py` currently has z1/z5 wing mapping inverted relative to the prompt — needs fixing.

## 8. Visualizer Features

- **Video panel**: Synced playback from local files or S3 presigned URLs
- **Court simulation**: 14-zone polygonal rendering with player markers
- **Unified timeline**: Physics frames (with transition chips) + inferred events
- **Filters**: All / Changes only / Events only
- **Auto-scroll**: Active frame/event always visible in timeline
- **Responsive**: CSS Grid layout, ResizeObserver for canvas sizing

## 9. Test Suite

| File | Tests | Coverage |
|------|-------|----------|
| `tests/test_team_classifier.py` | 21 | All 4 signals, GK detection, edge cases, JDF regression |
| `tests/test_event_detector.py` | 17 | Pass (via In-Air, direct, chain), shot, turnover, move |
| `tests/test_role_assigner.py` | 14 | Zone→x mapping, wing/pivot/back assignment, no duplicates |
| `tests/test_physics_to_events.py` | 7 | End-to-end pipeline, JDF regression, edge cases |

Run: `pytest tests/ -v`

## 10. Recent Changes (Feb 2026)

| Issue | Description | Status |
|-------|-------------|--------|
| #33 | z1/z5 wing mapping inverted in role_assigner.py | Open |
| #32 | Team classifier: infer attack/defense from physics signals | Closed |
| #31 | Fix pass detection, role assignment, add test suite | Closed |
| #30 | Unified timeline showing physics frames + inferred events | Closed |
| #29 | Visualizer overhaul: 14-zone system, responsive layout | Closed |

## 11. Environment Variables
```bash
GEMINI_API_KEY=your-key-here   # Required for Stage 1
AWS_ACCESS_KEY_ID=...          # Optional: for S3 video streaming
AWS_SECRET_ACCESS_KEY=...      # Optional: for S3 video streaming
```

## 12. Next Actions
1. Run pipeline on more test videos to validate team classifier across different matches
2. Improve physics prompt for better jersey number detection
3. Add support for tracking player movements across longer sequences
4. Implement batch processing for multiple videos
