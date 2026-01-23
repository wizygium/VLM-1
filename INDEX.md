# Project Index: VLM-1 Verification App

## Core Application
| File | Description |
|---|---|
| `verification_app/server.py` | **Main Backend.** FastAPI server. Handles job queue, VLM inference trigger, frame extraction, and API endpoints. |
| `src/vlm_1/processor.py` | **VLM Engine.** Wraps `mlx-community/Qwen2.5-VL`. Handles model loading, prompt construction, and *sequential batch processing* logic. |

## Frontend (Web UI)
| File | Description |
|---|---|
| `verification_app/static/index.html` | **Main UI.** Video input, job controls, status dashboard, and verification interface. |
| `verification_app/static/app.js` | **Frontend Logic.** Polls server for status, renders results, handles "Verify" clicks, and manages API communication. |
| `verification_app/static/style.css` | **Styling.** Dark mode CSS details for the dashboard. |

## Configuration & Data
| File | Description |
|---|---|
| `stats.json` | JSON schema definition / template for the VLM output. |
| `match_context.json` | Sample external context file (Teams, Scores) injected into the prompt. |
| `GerIsl.json`, `JapArg.json` | specific match context files. |
| `verification_app/data/` | **Storage.** Contains job subfolders (frames, clips) and the global `verification_results.json`. |
| `pyproject.toml` | Python dependencies and project metadata. |

## Documentation
| File | Description |
|---|---|
| `LEARNINGS.md` | **Critical Knowledge Base.** Insights on prompt engineering, MLX memory limits, and batch optimization strategies. |
| `HANDOVER.md` | **Start Here.** Summary of current state and next steps for new developers. |
| `task.md` | Active task tracking list. |
| `walkthrough.md` | Narrative guide of recent changes and features. |

## Scripts
| File | Description |
|---|---|
| `analyze_handball.py` | Legacy/CLI entry point script (superseded by `server.py`). |
