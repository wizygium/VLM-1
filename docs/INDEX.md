# Project File Index

## 📂 Root Directory
| File | Description |
|---|---|
| `gemini_cache_analyzer_v2.py` | **Main Script (Stage 1)**: VLM-based physics extraction (16fps). |
| `physics_to_events.py` | **Main Script (Stage 2)**: Event inference and roster generation. |
| `process_s3_handball.sh` | **Pipeline Script**: Orchestrates S3 download, Stage 1, and Stage 2. |

## 📂 Directories
| Directory | Description |
|---|---|
| `data/` | **Workspace**: Contains input `videos/` and output `analyses/`. |
| `docs/` | **Documentation**: Guides, definitions, and this index. |
| `physics_visualizer/` | **Web App**: Visualizer for analysis results (server.py + static). |
| `inference/` | **Logic**: Helper modules for event detection and role assignment. |
| `prompts/` | **Prompts**: Markdown system instructions for the VLM. |
| `archive/` | **Legacy**: Old scripts, logs, and results. |

## 📄 Documentation (in `docs/`)
| File | Description |
|---|---|
| `HANDOVER.md` | **Start Here**: Project overview and architecture. |
| `QUICKSTART.md` | **Usage**: Commands to run the pipeline. |
| `CLAUDE.md` | **Dev Guide**: Rules of engagement and detailed commands. |
| `LEARNINGS.md` | **Knowledge**: Insights on VLM behavior and optimization. |
| `DEBUG_VISUALIZER.md` | Troubleshooting guide for the visualizer. |
| `json_format.md` | Schema definition for physics and events JSON. |

## 📦 Archived (in `archive/`)
- `gemini_batch_analyzer.py` (Legacy V1)
- `gemini_physics_analyzer.py` (Legacy V1)
- `openrouter_analyzer.py` (Experiment)
- `results_legacy/` (Old test runs)
