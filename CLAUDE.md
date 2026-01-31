# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VLM-1 is a **Video Language Model (VLM) pipeline** for analyzing handball match footage. It supports multiple VLM backends and generates structured JSON output with spatial zone tracking (0-13), defensive formations (DL1-DR1), and event classification (PASS, SHOT, MOVEMENT).

**Domain:** Handball tactical analysis with precise spatial tracking and role-based player identification.

## Development Commands

### Environment Setup
```bash
# Install dependencies (uses hatchling)
pip install -e .
pip install -e ".[dev]"  # Include pytest, ruff
```

### Running Analysis Pipelines

**MLX-VLM Web App** (Primary interface for local M-series chips):
```bash
# Start FastAPI server (http://127.0.0.1:8000)
.venv/bin/python3 verification_app/server.py
```

**Gemini Cached Pipeline** (For Gemini 3 Pro with timeout handling):
```bash
# Modular cached pipeline - splits analysis into 6 steps to avoid timeouts
python gemini_cache_analyzer.py videos/ -o results_cache -m gemini-3-pro-preview

# Requires google-genai SDK (v1 Beta), NOT google-generativeai
# pip install google-genai
```

**Gemini Batch Analyzer** (For standard Gemini models):
```bash
# Process directory of videos
python gemini_batch_analyzer.py videos/ -o results/ --context GerIsl.json

# Single video
python gemini_batch_analyzer.py video.mp4 -m gemini-2.0-flash-exp -v
```

**OpenRouter Pipeline** (Nvidia Nemotron, Qwen):
```bash
# Requires OPENROUTER_API_KEY env var
python openrouter_analyzer.py videos/ -o results_openrouter -m nvidia/nemotron-nano-12b-v2-vl:free
```

**Physics-Only Analyzer** (Gemini 3 Flash - NEW, Recommended):
```bash
# Local video files
python gemini_physics_analyzer.py video.mp4 -o results_physics/ -v

# Or stream directly from S3 (requires AWS credentials)
python gemini_s3_analyzer.py s3://bucket/video.mp4 -o results_physics/ -v

# Batch process all videos in S3 prefix
python gemini_s3_analyzer.py s3://bucket/videos/ --batch -o results_physics/ -v

# Validate physics output (schema, temporal, adjacency)
python validate_physics_output.py results_physics/video_physics.json

# Derive events programmatically (PASS/SHOT from physics facts)
python physics_to_events.py results_physics/video_physics.json -o results_physics/video_events.json -v

# View statistics
python physics_to_events.py results_physics/video_physics.json --stats
```

**Visualization & Validation**:
```bash
# Generate annotated video from JSON analysis
python visualize_analysis.py results/analysis.json -o output_annotated.mp4

# Validate JSON against schema
python validate_results.py results/analysis.json
```

### Testing & Linting
```bash
# Run tests
pytest

# Lint/format (using ruff with 100 char line length)
ruff check .
ruff format .
```

## Architecture

### 1. MLX-VLM Engine (Local Apple Silicon)
**Critical Files:**
- [src/vlm_1/processor.py](src/vlm_1/processor.py): Core VLM wrapper for `mlx-community/Qwen2.5-VL-7B-Instruct-4bit`
- [verification_app/server.py](verification_app/server.py): FastAPI backend with job queue, frame extraction, and verification API

**How it works:**
- Uses **sequential mini-batching** (batch size = 1) with cumulative image history to avoid Metal memory crashes on M-series chips
- Images resized to max **1536px** longest side to prevent `[metal::malloc]` buffer errors (~17GB limit)
- Dynamic prompt rewriting per frame to prevent hallucination
- WebUI allows manual verification of AI outputs stored in `verification_app/data/verification_results.json`

**Memory constraints:**
- MLX-VLM uses Native Dynamic Resolution - high-res grids can trigger >15K visual tokens
- Solution: Always resize final grid images before inference
- Model loads once and stays resident in RAM - do not reload per request

### 2. Gemini API Pipelines

**Cached Modular Pipeline** ([gemini_cache_analyzer.py](gemini_cache_analyzer.py)):
- **Problem:** Gemini 3 Pro's deep thinking process (>5 mins) causes standard API timeouts
- **Solution:** Create 1-hour cache context with video + full prompt baked in, then run 6 discrete analysis steps against cache:
  1. `0_verify`: Configuration check
  2. `1_roster_lock`: Identify players & roles (immutable)
  3. `2_ball_state`: Physics-only ball tracking timeline
  4. `3_defense_grid`: Independent defensive formation analysis
  5. `4_tactical_synthesis`: Combine layers into events
  6. `5_sanity_check`: Hallucination detection & correction
  7. `6_json`: Final structured output
- **SDK Requirement:** Must use `google-genai` (v1 Beta), NOT `google-generativeai`

**Batch Pipeline** ([gemini_batch_analyzer.py](gemini_batch_analyzer.py)):
- Standard upload-and-analyze flow for Gemini 1.5 Pro / 2.0 Flash
- Validates output against JSON schema
- Tracks API costs

**Physics-Only Pipeline** ([gemini_physics_analyzer.py](gemini_physics_analyzer.py)):
- **NEW:** Simplified 2-step pipeline for physics observation + programmatic event detection
- **Advantages:** 5-10x faster, zero hallucination, 16fps high-resolution tracking
- **Step 1 (VLM):** Track ball state (holder_track_id, zone, state) and player positions (track_id, zone, jersey_number) at 16fps
- **Step 2 (Python):** Derive PASS/SHOT events from physics state changes using [physics_to_events.py](physics_to_events.py)
- **Track ID System:** Persistent player IDs (t1, t2, t3...) with optional jersey numbers when readable
- **49-Zone System:** Fine-grained spatial tracking with 6 depth bands (6m-7m, 7m-8m, ..., 11m-12m) × 8 lateral positions
- **Adjacency Validation:** [validate_physics_output.py](validate_physics_output.py) ensures players only move to adjacent zones at 16fps
- **S3 Integration:** [gemini_s3_analyzer.py](gemini_s3_analyzer.py) streams videos from AWS S3 with automatic cleanup
- **See:** [README_PHYSICS_ANALYZER.md](README_PHYSICS_ANALYZER.md) and [README_S3_INTEGRATION.md](README_S3_INTEGRATION.md) for usage guides

### 3. Domain Knowledge Layer

**Master Prompt (Inference-Based):** [gemini_context_zones.md](gemini_context_zones.md)
- Defines **14 spatial zones** (z0-z13) mapped to handball court geometry
- Defines **7 defensive roles** (DL1, DL2, DL3, DR3, DR2, DR1, ADV)
- Enforces strict handball logic: passes are teammate-to-teammate, fake detection, shot outcome rules
- **Critical Rule:** All zone references must be strings with "z" prefix (e.g., `"zone": "z10"`, NOT `"zone": 10`)

**Physics-Only Prompt (NEW):** [physics_prompt.md](physics_prompt.md)
- Defines **49-zone system** (z0 + z{depth}_{lateral}, e.g., z3_4 = 8-9m depth, center)
- Track ID-based player tracking with optional jersey numbers
- NO event inference - only observable physics (ball holder, zones, states)
- Forbidden vocabulary list to prevent VLM hallucination
- Adjacency constraints enforced during validation

**Match Context Files:**
- [match_context.json](match_context.json), [GerIsl.json](GerIsl.json), [JapArg.json](JapArg.json): Team colors, jersey mappings, match metadata
- Injected into prompts to help VLM distinguish teams

### 4. Frontend (Web Verification App)
- [verification_app/static/index.html](verification_app/static/index.html): Video input, job controls, results dashboard
- [verification_app/static/app.js](verification_app/static/app.js): Polls server for status, renders verification UI
- [verification_app/static/style.css](verification_app/static/style.css): Dark mode styling

## Key Design Patterns & Constraints

### MLX-VLM (Apple Silicon) Constraints
1. **Batch Size = 1**: Process frames sequentially, passing cumulative history (`[Img1]`, then `[Img1, Img2]`, etc.)
2. **Image Resizing**: Always resize grid images to ≤1536px longest side before inference
3. **No Parallel Batching**: Do NOT attempt parallel multi-image inference - causes silent hangs or Metal buffer crashes
4. **Model Persistence**: Processor loads model once and reuses it - avoid reloading

### Prompt Engineering Best Practices (from LEARNINGS.md)
| Do | Don't |
|---|---|
| Describe the JSON schema | Provide example JSON output (causes copying) |
| Use simple field descriptions | Use template placeholders like `N or null` |
| Say "JSON only, no other text" | Expect strict formatting compliance |
| Use robust JSON extraction (regex) | Assume clean JSON output |
| Ask model to describe what it sees first | Jump straight to interpretation |
| Put team/context info at START of prompt | Bury context in the middle |

### Gemini 3 Pro Strategy
- Use **High-Density Caching** with modular prompts to avoid monolithic 600s+ transactions
- Create cache with full context, then run small discrete steps
- TTL = 1 hour (3600s)
- Explicitly prompt for "Depth" and "Gaps" in defense analysis step before asking for final JSON

## Common Workflows

### Adding a New VLM Provider
1. Create new analyzer script (e.g., `new_provider_analyzer.py`)
2. Implement frame extraction (use `cv2.VideoCapture` or reuse `processor.extract_frames()`)
3. Load [gemini_context_zones.md](gemini_context_zones.md) as base prompt
4. Inject match context from JSON files
5. Parse response with `extract_json()` utility (handles markdown code blocks)
6. Validate against schema in [handball_zones_definition.md](handball_zones_definition.md)

### Debugging Analysis Quality
1. Check [LEARNINGS.md](LEARNINGS.md) for known prompt engineering issues
2. Verify zone definitions match [gemini_context_zones.md](gemini_context_zones.md)
3. Use [visualize_analysis.py](visualize_analysis.py) to render analysis overlays on video
4. Common issues:
   - Fake pass detection: Check if prompt includes "LOOK AHEAD" instruction
   - Wrong team identification: Ensure "Observe Before Interpret" pattern in prompt
   - Zone teleportation: Add sanity check step to prompt
   - Dribble vs pass confusion: Explicitly define "In-Air (Bounce)" vs "In-Air (Pass)" states

### Modifying Handball Logic
- Edit [gemini_context_zones.md](gemini_context_zones.md) (master prompt)
- Update [verification_app/server.py](verification_app/server.py) (MLX-VLM prompt injection around line 118)
- Update ANALYSIS_TASKS dict in [gemini_cache_analyzer.py](gemini_cache_analyzer.py) and [openrouter_analyzer.py](openrouter_analyzer.py)
- Test with known sequences to verify logic changes

## Known Issues & Maintenance

### Server Maintenance
- **Log Rotation:** `server.log` grows indefinitely - needs rotation strategy
- **FFmpeg Zombies:** If server force-killed, run `pkill -9 -f ffmpeg` to clean up lingering processes
- **Browser Cache:** If UI doesn't update, hard refresh (Cmd+Shift+R on Mac)

### API Keys & Environment

**For GitHub Codespaces (Recommended):**
1. Add secrets at: Repository Settings → Secrets and variables → Codespaces
   - `GEMINI_API_KEY`: Get from https://aistudio.google.com/apikey
   - `OPENROUTER_API_KEY`: Get from https://openrouter.ai/keys (optional)
2. Rebuild Codespace after adding secrets
3. Verify with: `./verify_setup.sh`

**For Local Development:**
- Create `.env` file and add keys (never commit - already in [.gitignore](.gitignore))
- Or export as environment variables: `export GEMINI_API_KEY=your-key-here`

All scripts prioritize environment variables over `.env` files.

### Performance Notes
- **MLX-VLM (GPU/Metal):** 1-2s per frame after initial load
- **Ollama (CPU):** 10-30s per frame (legacy, not recommended)
- **Gemini 3 Pro (Cached):** >5 mins per analysis (use cached pipeline)
- **Gemini 3 Flash (Physics):** 30-60s per 15s clip (NEW - recommended for speed)
- **Gemini 2.0 Flash:** ~10-30s per analysis

## Documentation Files
- [HANDOVER.md](HANDOVER.md): Current state summary, onboarding guide for new agents
- [LEARNINGS.md](LEARNINGS.md): Critical knowledge base on prompt engineering, MLX memory limits, batch optimization
- [INDEX.md](INDEX.md): File reference guide
- [README_GEMINI_BATCH.md](README_GEMINI_BATCH.md): Gemini batch analyzer user manual
- [README_PHYSICS_ANALYZER.md](README_PHYSICS_ANALYZER.md): Physics-only analyzer guide with 49-zone system
- [README_S3_INTEGRATION.md](README_S3_INTEGRATION.md): AWS S3 streaming integration guide
