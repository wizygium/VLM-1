# JSON Format Specification

This document defines the two-stage JSON format for handball video analysis.

## Architecture Overview

```
┌──────────────────────┐     ┌──────────────────────┐     ┌──────────────────┐
│  Gemini Inference    │────▶│  Programmatic        │────▶│   Visualizer     │
│  (Physics Layer)     │     │  Inference (Stage 2) │     │   (Display)      │
└──────────────────────┘     └──────────────────────┘     └──────────────────┘
         │                            │                           │
         ▼                            ▼                           ▼
   *_physics.json              *_events.json               Reads *_events.json
   (Raw observations)          (Roles + Events)
```

---

## Stage 1: Physics JSON (`*_physics.json`)

**Purpose:** Raw, observable facts only. NO interpretation, NO role assignment.

> [!IMPORTANT]
> This layer contains ONLY what Gemini can directly observe:
> - Player positions (anonymous track IDs)
> - Ball location and state
> - Jersey numbers and team colors
> 
> Role (CB, LB, etc.) and events (PASS, SHOT) are inferred in Stage 2.

### Schema

```json
{
  "metadata": {
    "video": "path/to/video.mp4",
    "model": "gemini-3-pro-preview",
    "fps": 10.0,
    "total_frames": 50,
    "duration_seconds": 5.0
  },
  "frames": [
    {
      "frame_index": 0,
      "timestamp": 0.0,
      "ball": {
        "zone": 8,
        "state": "Holding",
        "holder_track_id": "T1"
      },
      "players": [
        {
          "track_id": "T1",
          "team": "attack",
          "zone": 8,
          "jersey_number": "18"
        },
        {
          "track_id": "T2",
          "team": "attack",
          "zone": 6,
          "jersey_number": "10"
        },
        {
          "track_id": "D1",
          "team": "defense",
          "zone": 3,
          "jersey_number": "34"
        }
      ]
    },
    {
      "frame_index": 1,
      "timestamp": 0.5,
      "ball": {
        "zone": 7,
        "state": "In-Air",
        "holder_track_id": null
      },
      "players": [ ... ]
    }
  ]
}
```

### Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `ball.zone` | int | Zone 0-13 (see zone system below) |
| `ball.state` | enum | `Holding`, `Dribbling`, `In-Air`, `Loose` |
| `ball.holder_track_id` | string\|null | Track ID of holder, **null when In-Air or Loose** |
| `players[].track_id` | string | Anonymous ID (T1, T2, D1, etc.) - persistent across frames |
| `players[].team` | string | `attack`, `defense`, `goalkeeper`, or `referee` |
| `players[].zone` | int | Zone 0-13 |
| `players[].jersey_number` | string\|null | Visible jersey number if readable |

---

## Stage 2: Events JSON (`*_events.json`)

**Purpose:** Enriched with roles and programmatically-derived events.

> [!TIP]
> Stage 2 adds:
> - **Role assignment** (CB, LB, RB, etc.) from player positions and movement
> - **Events** (PASS, SHOT, MOVE) by comparing consecutive frames
> - **Backwards compatibility** via `original_event` field

### Schema

```json
{
  "metadata": {
    "video": "path/to/video.mp4",
    "source_physics": "path/to/*_physics.json",
    "derived_at": "2026-02-07T11:30:00Z"
  },
  "roster": {
    "attack": [
      { "track_id": "T1", "role": "CB", "jersey_number": "18" },
      { "track_id": "T2", "role": "LB", "jersey_number": "10" }
    ],
    "defense": [
      { "track_id": "D1", "role": "DL1", "jersey_number": "34" }
    ]
  },
  "events": [
    {
      "event_id": 1,
      "type": "PASS",
      "start_time": 0.6,
      "end_time": 1.0,
      "from_track_id": "T1",
      "from_role": "CB",
      "from_zone": 8,
      "to_track_id": "T2",
      "to_role": "LB",
      "to_zone": 7
    },
    {
      "event_id": 2,
      "type": "MOVE",
      "start_time": 1.0,
      "end_time": 2.0,
      "track_id": "T2",
      "role": "LB",
      "from_zone": 7,
      "to_zone": 3
    },
    {
      "event_id": 3,
      "type": "SHOT",
      "start_time": 4.8,
      "end_time": 5.1,
      "from_track_id": "T2",
      "from_role": "LB",
      "from_zone": 3,
      "outcome": "GOAL"
    }
  ],
  "frames": [
    {
      "frame_index": 0,
      "timestamp": 0.0,
      "active_event_ids": [1],
      "ball": {
        "zone": 8,
        "state": "Holding",
        "holder_track_id": "T1"
      },
      "players": [
        {
          "track_id": "T1",
          "role": "CB",
          "team": "attack",
          "zone": 8,
          "jersey_number": "18"
        }
      ],
      "original_event": {
        "type": "PASS",
        "from_role": "CB",
        "from_zone": 8,
        "to_role": "LB",
        "to_zone": 7,
        "description": "Center Back passes to Left Back"
      }
    }
  ]
}
```

### Event Types

| Type | Trigger Condition |
|------|-------------------|
| `PASS` | `holder_track_id` changes AND prior `In-Air` state |
| `SHOT` | Ball trajectory enters zone 0 (goal) from attacker |
| `GOAL` | Ball enters zone 0 + verified net ripple |
| `SAVE` | Shot blocked by goalkeeper |
| `MOVE` | Player zone changes between frames |
| `DRIBBLE` | Same holder + zone changes + `Dribbling` state |

---

## Zone System (14-Zone)

Reference: [handball_zones_definition.md](file:///Users/lukewildman/Projects/VLM-1/handball_zones_definition.md)

```
                GOAL (DEFENDING)
    ═══════════════════════════════════════════
                        [0]
         ┌──────────────║──────────────┐
         │           (6m D)            │
         └──────────────║──────────────┘
              6m LINE (D-LINE)
    
    [1]  [2]  [ 3 ]  [ 4 ]  [5]      ← 6m-8m (Wing & Close Attack)
    
    [6]  [7]  [ 8 ]  [ 9 ]  [10]     ← 8m-10m (Back Court)
                9m LINE
    
         [11]    [12]    [13]        ← 10m+ (Deep Court)
    
                MIDCOURT
```

| Zone | Description |
|------|-------------|
| 0 | Goal area (goalkeeper position) |
| 1-5 | 6m-8m: Wing and close attack positions |
| 6-10 | 8m-10m: Back court / 9m line positions |
| 11-13 | 10m+: Deep court positions |

---

## Backwards Compatibility

The `*_events.json` format maintains the `original_event` field in each frame for backwards compatibility with legacy visualizer code. New code should use the top-level `events` array instead.
