# CLAUDE.md

## 🚨 RULES OF ENGAGEMENT (CRITICAL)
- **VERIFICATION FIRST**: NEVER close a GitHub issue or mark a master task as "Done" without explicit, typed user confirmation (e.g., "OK", "Verified", "Looks good").
- **NO PREMATURE CLOSURE**: PROHIBITED from using `gh issue close` in the same turn as a fix implementation.
- **PROCESS OVER SPEED**: If in doubt, ask for verification. User alignment is prioritized over task completion speed.

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
python archive/gemini_cache_analyzer.py data/videos/ -o archive/results_cache -m gemini-3-pro-preview

# Requires google-genai SDK (v1 Beta), NOT google-generativeai
# pip install google-genai
```

**Gemini Batch Analyzer** (For standard Gemini models):
```bash
# Process directory of videos
python archive/gemini_batch_analyzer.py data/videos/ -o archive/results/ --context data/match_context.json

# Single video
python archive/gemini_batch_analyzer.py data/videos/video.mp4 -m gemini-2.0-flash-exp -v
```

**OpenRouter Pipeline** (Nvidia Nemotron, Qwen):
```bash
# Requires OPENROUTER_API_KEY env var
python archive/openrouter_analyzer.py videos/ -o archive/results_openrouter -m nvidia/nemotron-nano-12b-v2-vl:free
```

**Two-Stage Physics→Events Pipeline (RECOMMENDED - Feb 2026):**
```bash
# Stage 1: Physics Observation (Gemini VLM, 16fps, track-based)
python gemini_cache_analyzer_v2.py data/videos/clip.mp4 --output data/analyses --verbose
# Output: *_physics.json with frames, ball state, player positions

# Stage 2: Event Inference (Python, instant)
python physics_to_events.py data/analyses/clip_physics.json --output data/analyses/clip_events.json
# Output: *_events.json with roster (roles), events (PASS/SHOT/MOVE), enriched frames

# Visualizer
cd physics_visualizer && python server.py
# Open http://127.0.0.1:8001
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
# Run full test suite (59 tests: team classifier, event detector, role assigner, integration)
pytest tests/ -v

# Run specific test file
pytest tests/test_team_classifier.py -v

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

**Two-Stage Physics→Events Pipeline** (RECOMMENDED):
- **Step 1 (VLM):** [gemini_cache_analyzer_v2.py](gemini_cache_analyzer_v2.py) tracks ball state (holder_track_id, zone, state) and player positions (track_id, zone, jersey_number, team colour) at 16fps. Output: `*_physics.json`.
- **Step 2 (Python):** [physics_to_events.py](physics_to_events.py) infers team roles and derives events. Output: `*_events.json`.
- **Ontological Separation**: Raw physics frames (observable facts) vs tactical events (inferred sequences). This reduces VLM hallucination and improves UI clarity.
- **Track ID System:** Persistent player IDs (t1, t2, t3...) with optional jersey numbers when readable.
- **14-Zone System:** z0 (goal), z1-z5 (6m-8m), z6-z10 (8m-10m), z11-z13 (10m+). See [physics_prompt.md](prompts/physics_prompt.md).
- **S3 Integration:** [gemini_s3_analyzer.py](gemini_s3_analyzer.py) streams videos from AWS S3 with automatic cleanup.

**Inference Modules** (`inference/`):
- [inference/team_classifier.py](inference/team_classifier.py): Multi-signal team classification. Scores each jersey colour using ball possession (0.45), GK proximity (0.25), zone depth (0.20), defensive formation (0.10) to determine attacking/defending teams. Never hardcode colour→role mappings.
- [inference/event_detector.py](inference/event_detector.py): State-machine event detection. Tracks `_last_holder` across In-Air frames to detect PASS, SHOT, TURNOVER (STEAL/LOST_BALL/OUT_OF_BOUNDS), and MOVE events.
- [inference/role_assigner.py](inference/role_assigner.py): Zone-based role assignment. Wings (z1/z5), pivot (z2-z4), backs (z6-z10 sorted L→R), defence (sorted L→R as DL1-DR1).

### 3. Domain Knowledge Layer

**Physics Prompt (Active):** [prompts/physics_prompt.md](prompts/physics_prompt.md)
- Defines **14-zone system** (z0-z13) for spatial tracking
- Track ID-based player tracking with optional jersey numbers and team colours
- NO event inference — only observable physics (ball holder, zones, states)
- Forbidden vocabulary list to prevent VLM hallucination
- **Critical Rule:** All zone references must be strings with "z" prefix (e.g., `"zone": "z10"`, NOT `"zone": 10`)

**Legacy Prompt (Archived):** [archive/prompts/gemini_context_zones.md](archive/prompts/gemini_context_zones.md)
- Was used by legacy pipelines (gemini_cache_analyzer v1, openrouter, batch analyzer)
- Contained event-level inference instructions (now handled by Python in Stage 2)
- Zone definitions were updated to 14 zones but the file is no longer loaded by active code

**Match Context Files:**
- [match_context.json](match_context.json), [GerIsl.json](GerIsl.json), [JapArg.json](JapArg.json): Team colors, jersey mappings, match metadata
- Injected into prompts to help VLM distinguish teams

### 4. Physics Visualizer (Primary UI)
- [physics_visualizer/server.py](physics_visualizer/server.py): FastAPI backend (port 8001), serves analysis JSON and video URLs
- [physics_visualizer/static/app.js](physics_visualizer/static/app.js): Timeline, event filtering, video sync, court updates
- [physics_visualizer/static/court-renderer.js](physics_visualizer/static/court-renderer.js): 14-zone polygonal court rendering with player markers
- [physics_visualizer/static/style.css](physics_visualizer/static/style.css): Dark mode, CSS Grid responsive layout
- [physics_visualizer/static/index.html](physics_visualizer/static/index.html): Three-panel layout (video, court, timeline)
- **Unified Timeline**: Shows physics frame cards (with transition chips for holder/zone/state changes) interleaved with inferred event cards. Filterable: All / Changes / Events.

### 5. Legacy Verification App (Archive)
- [verification_app/](verification_app/): MLX-VLM based web app for local Apple Silicon inference. Still functional but not the primary workflow.

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
3. Load [prompts/physics_prompt.md](prompts/physics_prompt.md) as base prompt
4. Inject match context from JSON files
5. Parse response with `extract_json()` utility (handles markdown code blocks)
6. Validate against schema in [handball_zones_definition.md](handball_zones_definition.md)

### Debugging Analysis Quality
1. Check [LEARNINGS.md](LEARNINGS.md) for known prompt engineering issues
2. Verify zone definitions match [prompts/physics_prompt.md](prompts/physics_prompt.md)
3. Use the physics visualizer to inspect frame-by-frame state and transitions
4. Run `pytest tests/ -v` to verify inference logic
5. Common issues:
   - **Wrong team classification**: Check `metadata.team_classification` in events JSON. The multi-signal classifier should handle most cases. If wrong, verify the physics JSON has correct team colours and ball holder tracking.
   - **Missing passes**: The EventDetector needs consecutive frames with different holders. Check for In-Air gaps that break the holder chain.
   - **Wrong roles**: Check zone-to-position mapping in `role_assigner.py`. z1=right wing, z5=left wing (attacker's perspective).
   - Fake pass detection: Check if prompt includes "LOOK AHEAD" instruction
   - Zone teleportation: Verify frame-to-frame zone changes are adjacent

### Modifying Handball Logic
- Edit [prompts/physics_prompt.md](prompts/physics_prompt.md) (active VLM prompt)
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
- [HANDOVER.md](HANDOVER.md): **Start here** — current state, architecture, and onboarding guide
- [QUICKSTART.md](QUICKSTART.md): Minimal commands to run the pipeline
- [LEARNINGS.md](LEARNINGS.md): Critical knowledge base on prompt engineering, team classification, MLX memory limits
- [docs/INDEX.md](docs/INDEX.md): File reference guide
- [docs/README_PHYSICS_ANALYZER.md](docs/README_PHYSICS_ANALYZER.md): Physics analyzer guide
- [docs/README_S3_INTEGRATION.md](docs/README_S3_INTEGRATION.md): AWS S3 streaming integration guide
- [docs/QUICKSTART_VISUALIZER.md](docs/QUICKSTART_VISUALIZER.md): Visualizer troubleshooting
