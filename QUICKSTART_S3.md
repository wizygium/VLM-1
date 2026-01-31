# Quick Start: Process Handball Videos from S3

## One-Line Setup

```bash
# 1. Configure AWS (one-time)
aws configure

# 2. Set Gemini API key (if not already in Codespace secrets)
export GEMINI_API_KEY='your-gemini-api-key-here'

# 3. Run the full pipeline
./process_s3_handball.sh s3://your-bucket/handball-videos/
```

That's it! The script will:
- ✅ Stream videos from S3 (no manual download)
- ✅ Run physics analysis with Gemini (16fps, 49-zone tracking)
- ✅ Validate outputs (adjacency, schema, temporal checks)
- ✅ Derive PASS/SHOT events programmatically
- ✅ Generate statistics summary
- ✅ Clean up temporary files automatically

## What You Need

### 1. AWS Credentials

```bash
aws configure
```

You'll be prompted for:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., us-east-1)
- Default output format (json)

### 2. Gemini API Key

**Option A: GitHub Codespaces Secrets (Recommended)**
1. Repository Settings → Secrets → Codespaces
2. Add `GEMINI_API_KEY` secret
3. Rebuild Codespace

**Option B: Environment Variable**
```bash
export GEMINI_API_KEY='your-key-from-aistudio.google.com'
```

## Usage Examples

### Single Video

```bash
./process_s3_handball.sh s3://my-bucket/game1.mp4
```

### All Videos in a Folder

```bash
./process_s3_handball.sh s3://my-bucket/handball-clips/
```

### Custom Output Directory

```bash
./process_s3_handball.sh s3://my-bucket/videos/ my_results/
```

## What Gets Created

```
results_physics/
├── game1_physics.json     # Raw physics observations (track IDs, zones, ball states)
├── game1_events.json      # Derived PASS/SHOT events
├── game2_physics.json
├── game2_events.json
└── ...
```

## Sample Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Handball Video Analysis Pipeline (S3 → Physics → Events)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Input:  s3://handball-games/2024/germany-iceland/
Output: results_physics

✓ Gemini API key configured
✓ AWS credentials configured

Mode: Batch processing (all .mp4 files in prefix)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Step 1: Physics Observation (VLM)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Found 3 videos to process

[1/3]
🎬 Processing: s3://handball-games/2024/germany-iceland/clip1.mp4
  Downloading from S3: s3://handball-games/2024/germany-iceland/clip1.mp4
  Downloaded: 15.2 MB
  Uploading to Gemini File API... Ready: files/xyz123
  Creating cache (FPS=16, Resolution=HIGH, Model=gemini-3-flash-preview)...
  Running physics observation...
  ✅ Physics JSON saved: clip1_physics.json
  ✅ Validation passed!
  ⏱️  Completed in 52.3s
  🗑️  Cleaned up temporary file

[2/3]
...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Step 2: Validating Physics Outputs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Validating clip1_physics.json...
✅ Validation passed! All physics constraints satisfied.
✓ Validation passed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Step 3: Deriving Events (Programmatic)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Deriving events for clip1...

🎯 Detected 8 events:
  PASS: 6
  SHOT: 2

Event details:
  1. PASS @ 2.125s: #25 → #12 (z3_4 → z2_5)
  2. PASS @ 3.875s: #12 → #7 (z2_5 → z1_8)
  3. SHOT @ 5.625s: #7 from z1_8
  ...

✅ Events saved to: clip1_events.json

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Step 4: Statistics Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

clip1_physics.json

📊 Physics Statistics:
  Frames: 240
  Duration: 15.00s
  Unique players (track IDs): 14
  Unique jerseys detected: 12

  Ball states:
    Holding: 45 (18.8%)
    Dribbling: 32 (13.3%)
    In-Air: 89 (37.1%)
    Loose: 74 (30.8%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Pipeline Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Results saved to: results_physics

Output files:
-rw-r--r-- 1 user user  45K Jan 31 10:23 clip1_events.json
-rw-r--r-- 1 user user 123K Jan 31 10:22 clip1_physics.json
-rw-r--r-- 1 user user  38K Jan 31 10:25 clip2_events.json
-rw-r--r-- 1 user user 118K Jan 31 10:24 clip2_physics.json
-rw-r--r-- 1 user user  42K Jan 31 10:27 clip3_events.json
-rw-r--r-- 1 user user 121K Jan 31 10:26 clip3_physics.json

✅ All validation checks passed!
```

## Manual Step-by-Step (If You Prefer)

```bash
# 1. Physics analysis from S3
python gemini_s3_analyzer.py s3://bucket/video.mp4 -o results/ -v

# 2. Validate
python validate_physics_output.py results/video_physics.json

# 3. Derive events
python physics_to_events.py results/video_physics.json \
    -o results/video_events.json -v

# 4. View stats
python physics_to_events.py results/video_physics.json --stats
```

## Troubleshooting

### "GEMINI_API_KEY not set"
```bash
export GEMINI_API_KEY='your-key-here'
```

### "AWS credentials not configured"
```bash
aws configure
# Enter your AWS Access Key ID, Secret Key, and region
```

### "Access Denied" on S3
Check that your AWS credentials have `s3:GetObject` and `s3:ListBucket` permissions for your bucket.

### "No .mp4 files found"
Make sure your S3 prefix ends with `/` for batch mode:
```bash
# Correct for batch mode
./process_s3_handball.sh s3://bucket/videos/

# Single video (no trailing slash needed)
./process_s3_handball.sh s3://bucket/videos/game.mp4
```

## Cost Estimate

For a typical 15-second handball clip:
- **Gemini API**: ~$0.001 (Flash model, ~75K tokens)
- **S3 Transfer**: Usually free (egress to internet)
- **100 clips**: ~$0.10

## Next Steps

After processing, you can:

1. **Analyze results in JSON**
   ```bash
   cat results_physics/game1_events.json | jq '.events'
   ```

2. **Upload results back to S3**
   ```bash
   aws s3 sync results_physics/ s3://output-bucket/analysis-results/
   ```

3. **Visualize** (if visualize_analysis.py supports 49-zone system)
   ```bash
   python visualize_analysis.py results_physics/game1_events.json \
       -o game1_annotated.mp4
   ```

## Getting Help

- Full documentation: [README_S3_INTEGRATION.md](README_S3_INTEGRATION.md)
- Physics analyzer guide: [README_PHYSICS_ANALYZER.md](README_PHYSICS_ANALYZER.md)
- Project overview: [CLAUDE.md](CLAUDE.md)
