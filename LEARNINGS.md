# VLM-1 Learnings: llama3.2-vision via Ollama

## Overview

This document captures key learnings from developing a video analysis pipeline using `llama3.2-vision` running locally via Ollama.

## Model Behavior

### Prompting Best Practices

| Do | Don't |
|---|---|
| Describe the JSON schema | Provide example JSON output |
| Use simple field descriptions | Use template placeholders like `N or null` |
| Say "JSON only, no other text" | Expect the model to follow formatting strictly |
| Use robust JSON extraction | Assume clean JSON output |

### The Example-Copying Problem

**Problem:** When given an example JSON in the prompt, llama3.2-vision copies it verbatim instead of analyzing the image.

```
# BAD - model copies this exactly
PROMPT = """OUTPUT ONLY JSON.
{"action":"shoot","team":"blue","shirt_number":7,"confidence":0.9}
What action is the player taking?"""

# Result: Every frame returns {"action":"shoot","team":"blue","shirt_number":7,"confidence":0.9}
```

**Solution:** Describe the schema without providing an example:

```python
# GOOD - model actually analyzes the image
PROMPT = """Look at this handball match frame. Find the player holding the ball.

Return ONLY a JSON object with these fields:
- action: what they're doing ("shoot", "pass", or "dribble")
- team: their jersey color
- shirt_number: number on jersey (integer or null)
- confidence: 0.0 to 1.0

JSON only, no other text."""
```

### Verbose Output Handling

Even with strict instructions, the model often returns explanatory text around the JSON. Always implement robust extraction:

```python
import re
import json

def extract_json(text: str) -> dict | None:
    # Try direct parse
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Find JSON anywhere in text
    match = re.search(r'\{[^{}]*"action"[^{}]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Handle markdown code blocks
    if "```" in text:
        for part in text.split("```"):
            cleaned = part.strip()
            if cleaned.startswith("json"):
                cleaned = cleaned[4:].strip()
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                continue

    return None
```

## Performance Considerations

### Memory Requirements

- `llama3.2-vision` (11B): ~7 GB RAM
- `llama3.2-vision:90b`: ~55 GB RAM

Check available memory before processing:

```python
import psutil

mem = psutil.virtual_memory()
available_gb = mem.available / (1024**3)
```

### Processing Speed

- Expect 10-30+ seconds per frame on CPU
- Use larger frame intervals (2-5s) for long videos
- Add progress indicators for user feedback

### Frame Extraction

- First frame at 0s may be a transition/black frame
- Use `--start` offset to skip problematic opening frames
- 1 frame per second is usually sufficient for action detection

## Ollama Integration

### Pre-loading Models

Keep models loaded for faster processing:

```bash
# Load and keep warm for 60 minutes
ollama run llama3.2-vision --keepalive 60m
# Ctrl+C to exit chat, model stays loaded
```

### Checking Model Status

```bash
ollama list  # See installed models
ollama ps    # See running models
```

## Video Analysis Tips

### Handball-Specific

- Actions to detect: shoot, pass, dribble
- Model can read team names from jerseys (e.g., "argentina")
- Shirt numbers are often not visible (expect many `null` values)
- Confidence varies significantly (0.0 to 1.0)

### General Sports Video

- Frame quality matters - blurry frames get low confidence
- Action detection works best during clear moments
- Multiple players in frame can confuse the model
- Be specific about which player to focus on ("player holding the ball")

## Code Structure

```
VLM-1/
├── pyproject.toml           # Package config
├── src/vlm_1/
│   ├── __init__.py
│   ├── processor.py         # VideoProcessor class
│   └── cli.py               # CLI with memory check
├── analyze_handball.py      # Handball-specific script
└── stats.json               # Output file
```

## Future Improvements

- [ ] Try different VLM models (e.g., llava, bakllava)
- [ ] Add batch processing for multiple videos
- [ ] Implement frame caching to avoid re-extraction
- [ ] Add visual output (annotated frames)
- [ ] Test with higher quality/resolution frames
