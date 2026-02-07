# VLM-1 Learnings: Ollama & MLX-VLM

## Overview

This document captures key learnings from developing a video analysis pipeline using `llama3.2-vision` (Ollama) and `Qwen2.5-VL` (MLX-VLM) running locally on Apple Silicon.

## Model Behavior

### Prompting Best Practices

| Do | Don't |
|---|---|
| Describe the JSON schema | Provide example JSON output |
| Use simple field descriptions | Use template placeholders like `N or null` |
| Say "JSON only, no other text" | Expect the model to follow formatting strictly |
| Use robust JSON extraction | Assume clean JSON output |
| Ask model to describe what it sees first | Jump straight to interpretation |
| Put team/context info at START of prompt | Bury context in the middle |

### The Example-Copying Problem

**Problem:** When given an example JSON in the prompt, VLMs often copy it verbatim instead of analyzing the image.

**Solution:** Describe the schema without providing an example. This forces the model to generate the data based on visual evidence rather than pattern matching the prompt.

### The "Observe Before Interpret" Pattern

**Problem:** When asked to identify teams by jersey color, the model often ignores the color mapping and guesses incorrectly.

**Solution:** Force the model to describe what it observes (jersey color) BEFORE interpreting (team name) in the JSON structure.

---

## MLX-VLM & Qwen2.5-VL (Apple Silicon)

### Transition from Ollama
Moving to `MLX-VLM` with `Qwen2.5-VL` provides significantly better performance on Apple M-series chips and handles high-resolution grids more effectively.

### The Metal Memory Limit (RuntimeError)
**Warning:** Qwen2.5-VL uses **Native Dynamic Resolution**, meaning it tries to process images as close to their original resolution as possible.
- **Problem:** A grid of 6 HD frames can result in an extremely high-resolution image (e.g., 5000px+ width).
- **Result:** The model attempts to generate a massive number of visual tokens (15,000+), triggering `[metal::malloc]` errors if the allocation exceeds the system limit (e.g., ~17GB on many Macs).
- **Fix:** Resize the final grid image so its longest side is at most **1536px**. This maintains enough detail for jersey numbers while keeping token counts manageable.

### Model Weight Downloads (AWS/CDN)
- `MLX-VLM` pulls model weights from Hugging Face, which uses **AWS CloudFront** as a CDN.
- If a process looks "stalled" with high CPU and no file activity, it may be stuck in a network timeout during weights download. Check `~/.cache/huggingface/hub` for progress.

---

## Multi-Frame Analysis Strategy (Key Breakthrough)

### The "Stalling" Issue
**Problem:** When processing a batch of >2 high-resolution images simultaneously, the MLX framework on M4 chips would often hang silently or crash due to memory pressure/token limits.

**Solution: Batch Size = 1 with Cumulative History**
Instead of processing frames in parallel:
1.  **Sequential Processing:** Analyze one frame at a time (`BATCH_SIZE = 1`).
2.  **Cumulative Context:** Maintain a growing list of `PIL.Images` (e.g., `[Img1]`, then `[Img1, Img2]`, etc.).
3.  **Stateful Generation:** Pass this entire history to the `mlx_vlm.utils.generate` function for *every* step.
    *   *Result:* The model "sees" the full movie sequence accumulating, allowing it to understand temporal flow (e.g., "The ball passed from Player A to Player B").

### Dynamic Prompt Rewriting
**Problem:** If you give a global prompt ("Analyze these 6 images") to a single-frame mini-batch, the model hallucinates the other 5 frames in its output.

**Solution:** dynamically rewrite the prompt for each step:
-   **Step 1:** "This is the first image... Return 1 object."
-   **Step 2+:** "Continue analyzing the next frame... Return 1 object."
-   **Regex Magic:** Use `re.sub` to injection these instructions into the prompt just before inference.

---

## Domain Logic: Handball Intelligence

### Role & Rule Injection
VLMs do not inherently know strict sports rules. You must "teach" them in the prompt:
1.  **Define Roles:** Explicitly map court positions to roles (e.g., "Player in corner = Winger (LW/RW)").
2.  **Enforce Logic:** State rules as constraints (e.g., "Passes are almost ALWAYS between TEAMMATES").
3.  **Shot Outcomes:** Force the model to look for net movement or goalie blocks to distinguish Goals from Saves.

---

## Performance Considerations

### Speed Comparison
- **Ollama (CPU):** 10-30s per frame.
- **MLX-VLM (GPU/Metal):** 1-2s per frame (after initial load).

### Storage vs. Speed
- **Video Clips:** Extracting short (0.5s) clips instead of full events saves massive disk space and makes the verification UI snappy.
- **Global Persistence:** Store all verification results in a single `json` file (`verification_results.json`) rather than scattering them. This allows for "Resume" functionality.

## Future Improvements
- [x] Implement MLX-VLM for GPU acceleration
- [x] Add dynamic context loading (external JSON files)
- [x] Implement image resizing to prevent Metal buffer errors
- [x] **Solve Batch Stalling with Sequential Context**
- [x] **Implement Strict Sports Domain Logic**
- [ ] Add batch processing for directory of videos
- [ ] Implement frame caching

## Ontological Separation: Physics vs. Tactical Events (Feb 2026)

### The "Observation Overload" Problem
**Problem:** Asking a VLM to simultaneously track ball physics (zones, states) and tactical events (Passes, Shots) leads to "semantic bleed." The model might hallucinate a pass because it sees the ball in the air, or miss a pass because it's too focused on zone numbers.

### The Solution: Layered Extraction
1. **Raw Physics Layer (Observation)**:
    - **VLM's Job**: Tell us *what* it sees per frame (e.g., "Ball: Air", "Holder: t5").
    - **Focus**: High temporal resolution (16fps), spatial zones, and track IDs.
    - **Output**: `physics.json` (continuous record of facts).
2. **Tactical Event Layer (Inference)**:
    - **Python/Logic Job**: Look at the `physics.json` timeline and *infer* events (e.g., "Ball state change Hand -> Air -> Hand = PASS").
    - **Focus**: Tactical meaning, outcomes (Goal/Miss), and sequence grouping.
    - **Output**: `events.json` (discrete historical records).

### Why this works:
- **Reduces Hallucination**: Programmatic derivation of a pass is 100% accurate if the physics tracking is correct.
- **Improved UI Density**: Visualizers can now distinguish between "Raw State" (highlighting current zone) and "Event State" (contextual tactical cards).
- **Rethinking 'MOVE'**: A 'MOVE' should represent a tactical shift (e.g., player entering a new zone) rather than just a ball-in-air physics state.

### Timeouts & Caching Strategy
- **Issue**: Gemini 3 Pro's "Thinking" process is deep and slow (often >5 mins), causing standard API timeouts.
- **Solution**: **High-Density Caching** with Modular Prompts.
    - Create a cache with the video + full context (`gemini_context_zones.md`) baked in (TTL 1h).
    - Run separate, smaller prompt steps (Setup, Defense, Timeline, JSON) against this cache.
    - This avoids the single monolithic 600s+ transaction.

### SDK Requirement
- **Critical**: Caching features require the **v1 Beta SDK** (`google-genai`), NOT the older `google-generativeai`.
    - Install: `pip install google-genai`
    - Import: `from google import genai`

### Defensive Analysis
- **Explicit Prompting**: To get accurate defense depth (6m vs 9m), create a dedicated analysis step asking specifically for "Depth" and "Gaps" before asking for the final JSON.

### Visualization Enhancements
- **Geometry**: Draw accurate Handball court lines (Quarter-Arcs + Straight lines), don't approximate with semi-circles.
- **Orientation**: Ensure X-axis is "Attacker POV" (Left = Positive X) if that's how the user thinks.
- **Off-Ball Logic**: Distinguish `MOVEMENT` events with a `with_ball` boolean to visualize cuts (dotted lines) vs drives (solid lines).

## Two-Stage Pipeline Refinements (Feb 2026)

### Track-Based Physics Prompts
**Problem:** Using role names (LW, CB, PV) in VLM prompts causes semantic bleed - the model tries to infer tactical meaning instead of just observing.

**Solution:** Strip all role references from physics prompts:
- Use track IDs: t1, t2, t3... (assigned by order of appearance)
- Use team colors: "blue", "white", "yellow" (from jersey)
- Use zones: z0, z1, z2... (spatial position)
- VLM reports ONLY what it sees, never infers roles

### Stage 2 Role Assignment
**Learning:** Roles should be inferred programmatically from zones:
- z10, z11 = Wings (LW, RW)
- z9 = CB zone
- z8 = LB zone
- z7 = RB zone
- z2, z3 = Pivot zones (PV)
- z0, z1 = Defensive zones (DL1, DL2, etc.)

### Event Format Changes
**Critical:** Events now use `start_time` and `end_time` instead of single `time`:
```json
{"type": "PASS", "start_time": "1.0", "end_time": "1.5", "from_role": "CB", "to_role": "LB"}
```

Visualizer code must handle this:
```javascript
time: e.start_time || e.time  // Fallback for backwards compatibility
```

### FPS Optimization
**Discovery:** 16 FPS is optimal for handball:
- Fast enough to capture passes (ball in air ~0.5s)
- Slow enough to avoid redundant frames
- Matches typical broadcast frame intervals

### Browser Cache Traps
**Issue:** After updating JS/CSS, browser serves cached versions causing confusion.
**Fix:** Always hard refresh (Cmd+Shift+R) or disable cache in DevTools during development.

### Roster Display Logic
**Pattern:** Use Phase 2 roster data directly for player cards:
```javascript
if (eventsData?.roster) {
    renderRoster(eventsData.roster);  // Preferred: uses inferred roles
    return;
}
// Fallback: build from physics frames (no roles)
```

### Project Reorganization (Feb 2026)
- **Centralized Data:** Moving all data to a dedicated `data/` workspace (`data/videos`, `data/analyses`) simplifies path management and separation of concerns.
- **Archiving:** Aggressively archiving legacy scripts (`archive/`) reduces cognitive load and prevents accidental usage of outdated pipelines.
- **Documentation:** Grouping non-essential docs into `docs/` keeps the root clean and focused on the active entry points.
