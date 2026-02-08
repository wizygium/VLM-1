# Project File Index

## Root Directory (Active Entry Points)
| File | Description |
|---|---|
| `gemini_cache_analyzer_v2.py` | **Main Script (Stage 1)**: VLM-based physics extraction (16fps). |
| `physics_to_events.py` | **Main Script (Stage 2)**: Team classification, event inference, roster generation. |
| `process_s3_handball.sh` | **Pipeline Script**: Orchestrates S3 download, Stage 1, and Stage 2. |
| `CLAUDE.md` | **Agent rules**: Development commands, architecture, key constraints. |
| `HANDOVER.md` | **Onboarding**: Current state, architecture diagram, quick start. |
| `QUICKSTART.md` | **Quick start**: Minimal commands to run the pipeline. |
| `LEARNINGS.md` | **Knowledge base**: VLM behaviour, team classification, design decisions. |

## Inference Modules (`inference/`)
| File | Description |
|---|---|
| `inference/__init__.py` | Package exports for all inference modules. |
| `inference/team_classifier.py` | Multi-signal team classification (possession, GK, depth, formation). |
| `inference/event_detector.py` | State-machine event detection (PASS, SHOT, TURNOVER, MOVE). |
| `inference/role_assigner.py` | Zone-based role assignment (LW/RW/PV/LB/CB/RB, DL1-DR1). |

## Prompts (`prompts/`)
| File | Description |
|---|---|
| `prompts/physics_prompt.md` | **Active** VLM system instruction: 14-zone track-based physics observation. |

## Physics Visualizer (`physics_visualizer/`)
| File | Description |
|---|---|
| `physics_visualizer/server.py` | FastAPI backend (port 8001), serves analyses and video URLs. |
| `physics_visualizer/static/index.html` | Three-panel layout: video, court simulation, timeline. |
| `physics_visualizer/static/app.js` | Timeline rendering, event filtering, video sync, court updates. |
| `physics_visualizer/static/court-renderer.js` | 14-zone polygonal court rendering with player markers. |
| `physics_visualizer/static/style.css` | Dark mode styling, CSS Grid responsive layout. |
| `physics_visualizer/static/zone-editor.html` | Standalone tool for drawing custom zone boundaries. |

## Tests (`tests/`)
| File | Tests | Description |
|---|---|---|
| `tests/conftest.py` | — | Shared fixtures (`build_physics_json` factory). |
| `tests/test_team_classifier.py` | 21 | All 4 signals, GK detection, edge cases, JDF regression. |
| `tests/test_event_detector.py` | 17 | Pass (via In-Air, direct, chain), shot, turnover, move. |
| `tests/test_role_assigner.py` | 14 | Zone-to-x mapping, wing/pivot/back assignment, no duplicates. |
| `tests/test_physics_to_events.py` | 7 | End-to-end pipeline, JDF-Scene-001 regression, edge cases. |

## Data (`data/`)
| Directory | Description |
|---|---|
| `data/videos/` | Input video files (MP4). |
| `data/analyses/` | Output JSON files (`*_physics.json`, `*_events.json`, `*_report.md`). |
| `data/analyses/TEST-*_physics.json` | Synthetic test fixtures for visual verification. |

## Documentation (`docs/`)
| File | Description |
|---|---|
| `docs/INDEX.md` | This file — project file reference. |
| `docs/QUICKSTART_VISUALIZER.md` | Visualizer troubleshooting guide. |
| `docs/QUICKSTART_S3.md` | S3 integration quick start. |
| `docs/README_PHYSICS_ANALYZER.md` | Physics analyzer detailed guide. |
| `docs/README_S3_INTEGRATION.md` | AWS S3 streaming integration guide. |
| `docs/README_GEMINI_BATCH.md` | Legacy Gemini batch analyzer manual. |
| `docs/README_VISUALIZER.md` | Visualizer feature documentation. |

## Archived (`archive/`)
- `gemini_batch_analyzer.py` (Legacy V1)
- `gemini_cache_analyzer.py` (Legacy V1 cached pipeline)
- `gemini_physics_analyzer.py` (Legacy V1 physics pipeline)
- `openrouter_analyzer.py` (Experiment)
- `archive/prompts/gemini_context_zones.md` (Legacy prompt, replaced by `prompts/physics_prompt.md`)
- `results_legacy/` (Old test runs)
