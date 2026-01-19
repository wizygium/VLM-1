# Gemini Batch Video Analyzer

Batch process handball video scenes using Gemini 3 Pro API with advanced zone and defensive formation tracking.

## Features

- ✅ **Batch Processing**: Analyze multiple videos automatically
- ✅ **Smart Upload**: Video upload to Gemini File API
- ✅ **Advanced Schema**: Zones (0-13) + Defensive formations (D1-D6)
- ✅ **JSON Validation**: Automatic schema validation
- ✅ **Cost Tracking**: Estimate API costs
- ✅ **Error Handling**: Retry logic and detailed error reporting

## Setup

### 1. Install Dependencies

```bash
pip install google-generativeai jsonschema click tqdm
```

Or if using the project:
```bash
pip install -e .
```

### 2. Get API Key

1. Visit https://aistudio.google.com/apikey
2. Create a new API key
3. Set environment variable:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

Or create a `.env` file:
```bash
cp .env.example .env
# Edit .env and add your API key
```

## Usage

### Basic Usage

```bash
# Analyze single video
python gemini_batch_analyzer.py GI17scenes-Scene-011.mp4

# Analyze all videos in directory
python gemini_batch_analyzer.py videos/

# Specify output directory
python gemini_batch_analyzer.py videos/ -o results/
```

### With Match Context

```bash
# Include team/match information
python gemini_batch_analyzer.py videos/ --context GerIsl.json
```

Where `GerIsl.json` contains:
```json
{
  "match": "Germany vs Iceland - Friendly 2025",
  "teams": [
    {"color": "WHITE", "name": "GERMANY"},
    {"color": "BLUE", "name": "ICELAND"}
  ]
}
```

### Advanced Options

```bash
# Use Gemini 2.0 Flash (faster, cheaper, experimental)
python gemini_batch_analyzer.py videos/ --model gemini-2.0-flash-exp

# Verbose output
python gemini_batch_analyzer.py videos/ -v

# Custom context prompt
python gemini_batch_analyzer.py videos/ --prompt custom_prompt.md
```

## Output

### File Structure

```
results/
├── GI17scenes-Scene-011_analysis.json
├── JDF-Scene-011_analysis.json
├── batch_summary.json
```

### Individual Analysis File

```json
{
  "video_file": "GI17scenes-Scene-011.mp4",
  "processed_at": "2026-01-18T14:35:00Z",
  "model": "gemini-1.5-pro",
  "analysis": [
    {
      "video": "GI17scenes-Scene-011.mp4"
    },
    {
      "frame": {
        "time": "0.00 seconds",
        "possession": {
          "team": "WHITE",
          "player_role": "RB",
          "zone": 10,
          "action": "Pass"
        },
        "event": {
          "type": "PASS",
          "from_role": "RB",
          "from_zone": 10,
          "to_role": "CB",
          "to_zone": 8,
          "description": "..."
        },
        "defensive_formation": {
          "formation_type": "6-0 sliding",
          "defenders": {
            "D1": 1,
            "D2": 2,
            "D3": 3,
            "D4": 4,
            "D5": 5,
            "D6": 3
          }
        },
        "game_state": "Attacking"
      }
    }
  ],
  "validation": {
    "passed": true,
    "errors": []
  }
}
```

### Batch Summary

```json
{
  "total_videos": 10,
  "successful": 9,
  "failed": 1,
  "model": "gemini-1.5-pro",
  "estimated_cost_usd": 0.25,
  "errors": []
}
```

## Cost Estimates

Approximate costs per video (6-second scene):

| Model | Cost per scene |
|-------|----------------|
| Gemini 1.5 Pro | ~$0.0005 |
| Gemini 2.0 Flash | ~$0.0001 |

**Example**: 100 scenes × 6 seconds = 10 minutes
- Gemini 1.5 Pro: ~$0.05 USD
- Gemini 2.0 Flash: ~$0.01 USD

## Validation

The script automatically validates:
- ✅ JSON structure
- ✅ Required fields (time, possession, event, defensive_formation)
- ✅ Zone numbers (0-13)
- ✅ Defensive roles (D1-D6)
- ✅ Event types (PASS, MOVEMENT, SHOT)

Validation warnings are shown but don't stop processing.

## Troubleshooting

### API Key Issues
```
Error: GEMINI_API_KEY not set
```
**Solution**: Set environment variable or use `--api-key` flag

### Video Upload Fails
```
RuntimeError: Video processing failed
```
**Solution**: Check video format (MP4), size (<2GB), and internet connection

### Invalid JSON Response
```
ValueError: Failed to parse JSON response
```
**Solution**: Check that `gemini_context_zones.md` is correctly formatted. The model should output JSON only.

## Command Reference

```bash
python gemini_batch_analyzer.py [OPTIONS] INPUT_PATH

Arguments:
  INPUT_PATH  Video file or directory of videos

Options:
  -o, --output DIR         Output directory (default: results/)
  -c, --context FILE       Match context JSON file
  -p, --prompt FILE        Context prompt file (default: gemini_context_zones.md)
  -m, --model NAME         Model name (default: gemini-1.5-pro)
  --api-key KEY           API key (or set GEMINI_API_KEY env var)
  -v, --verbose           Verbose output
  --help                  Show help message
```

## Schema Reference

See [`gemini_context_zones.md`](gemini_context_zones.md) for complete schema documentation including:
- Zone definitions (0-13)
- Defensive roles (D1-D6)
- Event types (PASS, MOVEMENT, SHOT)
- Spatial continuity rules
