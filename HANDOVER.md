# Handover Document: VLM-1 Handball Analysis Pipeline

**Date:** 2026-02-07
**Status:** Operational (Two-Stage Physics→Events Pipeline)

## 1. Project Overview
This project is a **Video Language Model (VLM) Pipeline** for analyzing Handball matches. It uses Gemini 3 Pro for video analysis and outputs structured JSON with spatial tracking and event detection.

**Key Innovation:** Two-stage pipeline separating physics observation (VLM) from event inference (Python).

## 2. Current Architecture

### Two-Stage Pipeline
```
Stage 1: Physics Observation (Gemini VLM)
├── Input: Video file (MP4)
├── Output: *_physics.json
├── Content: Raw observations at 16fps
│   - Ball: holder_track_id, zone, state (Holding/In-Air/Loose)
│   - Players: track_id, zone, jersey_number, team color
│   - NO role inference, NO event detection
└── Script: gemini_cache_analyzer_v2.py

Stage 2: Event Inference (Python)
├── Input: *_physics.json
├── Output: *_events.json
├── Content: Programmatic derivation
│   - Roster with inferred roles (RW, CB, LB, PV, DL1, DL2...)
│   - Events: PASS, SHOT, MOVE with start_time/end_time
│   - Frames enriched with roles and active_event_ids
└── Script: physics_to_events.py
```

### Why Two Stages?
- **Reduces Hallucination**: VLM only reports what it sees, doesn't guess events
- **100% Accurate Events**: Pass detection from physics state changes is deterministic
- **Cleaner UI**: Clear separation of raw state vs tactical interpretation

## 3. Quick Start

### Run Full Pipeline
```bash
# Stage 1: Physics (runs Gemini, ~3 mins per video)
python gemini_cache_analyzer_v2.py videos/clip.mp4 --output results_physics --verbose

# Stage 2: Events (runs locally, instant)
python physics_to_events.py results_physics/clip_physics.json --output results_physics/clip_events.json
```

### Visualizer
```bash
cd physics_visualizer
python server.py
# Open http://127.0.0.1:8001
```

## 4. Key Files

| File | Purpose |
|------|---------|
| `gemini_cache_analyzer_v2.py` | Stage 1: VLM physics extraction (16fps) |
| `physics_to_events.py` | Stage 2: Event inference from physics |
| `prompts/physics_prompt.md` | System instruction for VLM |
| `inference/role_assigner.py` | Role inference logic (zones→roles) |
| `inference/event_detector.py` | Event detection logic |
| `physics_visualizer/` | Web UI for viewing results |

## 5. JSON Formats

### Physics JSON (Stage 1)
```json
{
  "fps": 16.0,
  "frames": [
    {
      "timestamp": "1.000",
      "ball": {"holder_track_id": "t5", "zone": "z9", "state": "Holding"},
      "players": [
        {"track_id": "t5", "zone": "z9", "jersey_number": "23", "team": "blue"}
      ]
    }
  ]
}
```

### Events JSON (Stage 2)
```json
{
  "roster": {
    "attack": [{"track_id": "t5", "role": "CB", "jersey_number": "23"}],
    "defense": [{"track_id": "t2", "role": "DL1", "jersey_number": "14"}]
  },
  "events": [
    {"event_id": 1, "type": "PASS", "start_time": "1.0", "end_time": "1.5", "from_role": "CB", "to_role": "LB"}
  ],
  "frames": [/* frames with roles and active_event_ids */]
}
```

## 6. Known Issues (See GitHub Issues)

| Issue | Description |
|-------|-------------|
| #1 | Video playback failure in visualizer (S3 URL issue) |
| #25 | Defender display (now fixed with Phase 2 roster) |
| #27 | UI needs compact layout (no scrolling) |
| #28 | Project folder reorganization needed |

## 7. Environment Variables
```bash
GEMINI_API_KEY=your-key-here  # Required for Stage 1
```

## 8. Next Actions
1. Run pipeline on more test videos
2. Implement compact visualizer layout (#27)
3. Reorganize project folders (#28)
4. Fix video playback (#1)
