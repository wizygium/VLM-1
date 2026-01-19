# Handover Document: VLM-1 Verification App

**Date:** 2026-01-17
**Status:** Operational (Stable VLM Inference)

## 1. Project Overview
This project is a **Video Language Model (VLM) Pipeline** for analyzing Handball matches. It runs locally on Apple Silicon (M4) using `mlx-community/Qwen2.5-VL-7B-Instruct-4bit`.
It features a **Web UI** for users to trigger analysis jobs and manually verify the AI's output.

## 2. Current State
- **Backend:** FastAPI server (`verification_app/server.py`) managing a single-threaded VLM worker.
- **Frontend:** HTML/JS Dashboard (`http://127.0.0.1:8000`) for job control and results review.
- **Stability:** Solved major "hanging" issues by implementing **Sequential Mini-Batching** (Batch Size = 1) with cumulative context history.
- **Accuracy:** Implemented "Handball Intelligence" in the prompt (Roles like RB/CB/PV, strict teammate passing logic).

## 3. How to Run
1.  **Start Server:**
    ```bash
    .venv/bin/python3 verification_app/server.py
    ```
2.  **Access UI:** Open `http://127.0.0.1:8000` in Chrome/Safari.
3.  **Run Analysis:**
    -   Paste video path (e.g., `/Users/.../video.mp4`).
    -   Set Offset (e.g., `0`) and Max Frames (e.g., `18`).
    -   Click "Start Analysis".

## 4. Key Logic (Must Read)
-   **Sequential Batching (`src/vlm_1/processor.py`):** The model processes frames *one at a time* to save RAM, but passes the *full history* of previous images to maintain context. Do not revert to parallel batching without testing M4 memory limits.
-   **Prompt Injection (`server.py`):** The prompt explicitly defines Handball Roles (GK, LW, RW, etc.). Any changes to logic should happen here.

## 5. Known Issues
-   **Server Logs:** The `server.log` file grows indefinitely. Needs a rotation strategy.
-   **FFmpeg Zombies:** Occasionally `ffmpeg` processes for clip extraction might linger if the server is force-killed. Run `pkill -9 -f ffmpeg` to clean up.
-   **Browser Cache:** If UI doesn't update, doing a Hard Refresh (Cmd+Shift+R) usually fixes it.

## 6. Next Actions for New Agent
1.  **Verify Full Batch:** Run a full 18-20 frame analysis to confirm long-term stability.
2.  **Tune Shot Logic:** Check if "Shot" detection is accurate (Goal vs Save). The current prompt has explicit rules for this, but needs empirical testing.
3.  **Enhance JSON Schema:** Add `from_role` and `to_role` to the output schema to enforce structured reasoning about passes.

## 7. Gemini 3 Pro Batch Pipeline (New - Jan 2026)

**Context**: We moved to a **Cached, Modular Pipeline** to handle Gemini 3 Pro's long thinking times.

### Scripts
- **`gemini_cache_analyzer.py`**: The primary script.
    - **Usage**: `python gemini_cache_analyzer.py videos/ -o results_cache -m gemini-3-pro-preview`
    - **Logic**: Creates a 1-hour cache context, then runs 4 discrete steps (Setup -> Defense -> Timeline -> JSON).
- **`visualize_analysis.py`**: The debugger.
    - **Usage**: `python visualize_analysis.py <json_file> -o <mp4_file>`
    - **Features**: Verified 6m/9m geometry, Off-Ball movement (dotted lines), PV2 role support.

### Key Prompts
- **`gemini_context_zones.md`**: The master prompt. Defines Zones 0-13, Roles (PV2), and Rules. This is injected into the Cache System Instruction.

### Next Tasks
1.  **Validation**: Run the cached analyzer on `test24` batch.
2.  **Refinement**: If defense depth is still vague, refine Step 2 in `gemini_cache_analyzer.py`.
