# VLM-1 Quick Start

## Prerequisites
```bash
export GEMINI_API_KEY=your-key-here
pip install google-genai click
```

## Run Pipeline

### Stage 1: Physics Extraction (Gemini VLM)
```bash
python gemini_cache_analyzer_v2.py videos/clip.mp4 --output results_physics --verbose
```
**Output:** `results_physics/clip_physics.json` - raw observations at 16fps

### Stage 2: Event Inference (Python)
```bash
python physics_to_events.py results_physics/clip_physics.json --output results_physics/clip_events.json
```
**Output:** `results_physics/clip_events.json` - roster with roles, detected events

## Visualizer
```bash
cd physics_visualizer
python server.py
# Open http://127.0.0.1:8001
```

## Key Files
| File | Purpose |
|------|---------|
| `gemini_cache_analyzer_v2.py` | Stage 1 VLM physics extraction |
| `physics_to_events.py` | Stage 2 event inference |
| `prompts/physics_prompt.md` | VLM system instruction |
| `physics_visualizer/` | Web visualization |

## Troubleshooting
- **API Error**: Check `GEMINI_API_KEY` is set
- **Visualizer cache**: Hard refresh (Cmd+Shift+R)
- **NaN timestamps**: Refresh browser to get latest JS
