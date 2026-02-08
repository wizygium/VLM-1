# VLM-1 Quick Start

## Prerequisites
```bash
export GEMINI_API_KEY=your-key-here
pip install -e ".[dev]"  # or: pip install google-genai click pytest
```

## Run Pipeline

### Stage 1: Physics Extraction (Gemini VLM)
```bash
python gemini_cache_analyzer_v2.py data/videos/clip.mp4 --output data/analyses --verbose
```
**Output:** `data/analyses/clip_physics.json` — raw observations at 16fps (ball state, player positions, team colours)

### Stage 2: Event Inference (Python, instant)
```bash
python physics_to_events.py data/analyses/clip_physics.json -v
```
**Output:** `data/analyses/clip_events.json` — team classification, roster with roles, detected events (PASS/SHOT/MOVE/TURNOVER)

Stage 2 automatically determines which team is attacking vs defending using physical signals (ball possession, goalkeeper proximity, zone depth, formation). No colour-to-role configuration needed.

## Visualizer
```bash
cd physics_visualizer && python server.py
# Open http://127.0.0.1:8001
```
Features: video playback, 14-zone court simulation, unified timeline (physics frames + inferred events), filter bar.

## Run Tests
```bash
pytest tests/ -v  # 59 tests: team classifier, event detector, role assigner, integration
```

## Key Files
| File | Purpose |
|------|---------|
| `gemini_cache_analyzer_v2.py` | Stage 1: VLM physics extraction |
| `physics_to_events.py` | Stage 2: team classification + event inference |
| `inference/` | Python inference modules (team_classifier, event_detector, role_assigner) |
| `prompts/physics_prompt.md` | VLM system instruction |
| `physics_visualizer/` | Web visualization |
| `tests/` | Pytest suite (59 tests) |
| `data/videos/` | Input videos |
| `data/analyses/` | Output JSONs |
| `HANDOVER.md` | Full architecture and onboarding guide |

## Troubleshooting
- **API Error**: Check `GEMINI_API_KEY` is set (`echo $GEMINI_API_KEY`)
- **Wrong teams**: Check `metadata.team_classification` in the events JSON — the classifier should handle it automatically
- **Visualizer cache**: Hard refresh (`Cmd+Shift+R`)
- **Missing dependencies**: `pip install fastapi uvicorn boto3`
