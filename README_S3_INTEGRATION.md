# S3 Integration for Physics Analyzer

Process handball videos directly from AWS S3 without manually downloading files. Videos are streamed to temporary storage, processed, and cleaned up automatically.

## Features

- **Stream from S3**: No need to download videos manually
- **Automatic cleanup**: Temporary files deleted after processing
- **Batch processing**: Process entire S3 prefixes in one command
- **Disk space efficient**: Only one video in temp storage at a time

## Prerequisites

```bash
# Install AWS SDK
pip install boto3

# Configure AWS credentials (one-time setup)
aws configure
# Or set environment variables:
# export AWS_ACCESS_KEY_ID=your-key
# export AWS_SECRET_ACCESS_KEY=your-secret
# export AWS_DEFAULT_REGION=us-east-1
```

## Usage

### Single Video

```bash
python gemini_s3_analyzer.py s3://your-bucket/handball/clip1.mp4 \
    -o results_physics/ -v
```

### Batch Process Entire S3 Prefix

```bash
# Process all .mp4 files in s3://your-bucket/handball/
python gemini_s3_analyzer.py s3://your-bucket/handball/ \
    --batch -o results_physics/ -v
```

### With Custom AWS Profile

```bash
# Use specific AWS profile from ~/.aws/credentials
python gemini_s3_analyzer.py s3://your-bucket/video.mp4 \
    --aws-profile my-profile -v
```

## Complete Workflow Example

```bash
# 1. List videos in your S3 bucket
aws s3 ls s3://your-bucket/handball-clips/

# 2. Process all videos in batch
python gemini_s3_analyzer.py s3://your-bucket/handball-clips/ \
    --batch -o results_physics/ -v

# 3. Validate outputs
for f in results_physics/*_physics.json; do
    echo "Validating $f"
    python validate_physics_output.py "$f"
done

# 4. Derive events from all physics files
for f in results_physics/*_physics.json; do
    base=$(basename "$f" _physics.json)
    echo "Deriving events for $base"
    python physics_to_events.py "$f" \
        -o "results_physics/${base}_events.json" -v
done

# 5. View statistics summary
for f in results_physics/*_physics.json; do
    echo "=== $(basename $f) ==="
    python physics_to_events.py "$f" --stats
    echo
done
```

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  1. S3 Download (streaming to temp)                         │
│     s3://bucket/video.mp4 → /tmp/tmpXXXX.mp4                │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Gemini Upload                                            │
│     /tmp/tmpXXXX.mp4 → Gemini File API                      │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Physics Analysis                                         │
│     16fps, HIGH resolution, track IDs, 49-zone system       │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Save Results                                             │
│     results_physics/video_physics.json                       │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Cleanup                                                  │
│     Delete /tmp/tmpXXXX.mp4                                  │
└─────────────────────────────────────────────────────────────┘
```

## Configuration Options

```bash
python gemini_s3_analyzer.py --help

Options:
  -o, --output TEXT         Output directory (default: results_physics)
  -m, --model TEXT          Model name (default: gemini-3-flash-preview)
  --api-key TEXT            Gemini API key (or set GEMINI_API_KEY env var)
  --aws-profile TEXT        AWS profile from ~/.aws/credentials
  -v, --verbose             Verbose output
  --batch                   Process all .mp4 files in S3 prefix
```

## Environment Variables

Required:
- `GEMINI_API_KEY`: Your Gemini API key

Optional:
- `AWS_ACCESS_KEY_ID`: AWS access key (or use `aws configure`)
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_DEFAULT_REGION`: AWS region (e.g., us-east-1)
- `AWS_PROFILE`: AWS profile name

## S3 Permissions Required

Your AWS credentials need these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket/*",
        "arn:aws:s3:::your-bucket"
      ]
    }
  ]
}
```

## Batch Processing Output

When using `--batch`, the script processes all `.mp4` files in the S3 prefix:

```
Found 15 videos to process

[1/15]
🎬 Processing: s3://bucket/handball/clip1.mp4
  Downloading from S3: s3://bucket/handball/clip1.mp4
  Downloaded: 12.3 MB
  Uploading to Gemini File API... Ready: files/abc123
  Creating cache (FPS=16, Resolution=HIGH, Model=gemini-3-flash-preview)...
  Running physics observation...
  ✅ Physics JSON saved: clip1_physics.json
  ✅ Validation passed!
  ⏱️  Completed in 45.2s
  🗑️  Cleaned up temporary file

[2/15]
🎬 Processing: s3://bucket/handball/clip2.mp4
...
```

## Cost Optimization

**Gemini API Costs** (approximate):
- 15-second clip at 16fps HIGH = ~75,000 tokens
- Flash model: ~$0.001 per 15s clip
- 100 clips: ~$0.10

**S3 Data Transfer**:
- Within same AWS region: Free egress to internet
- Cross-region: Standard AWS data transfer rates apply

**Recommendations**:
1. Process videos in batches to amortize API overhead
2. Use `gemini-3-flash-preview` (fast + cheap) instead of Pro models
3. Keep videos in same region as your processing machine if possible

## Troubleshooting

### AWS Authentication Errors

```
❌ S3 Download Error: NoCredentialsError
```

**Solution**: Configure AWS credentials
```bash
aws configure
# Or set environment variables
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
```

### S3 Access Denied

```
❌ S3 Download Error: ClientError: Access Denied
```

**Solution**: Check IAM permissions - need `s3:GetObject` and `s3:ListBucket`

### Gemini API Key Not Set

```
Error: GEMINI_API_KEY not set
```

**Solution**: Set environment variable
```bash
export GEMINI_API_KEY='your-gemini-api-key'
```

### Disk Space Issues

The script uses `/tmp` for temporary storage. If you see disk space errors:

```bash
# Check available space
df -h /tmp

# Clean up old temp files (if needed)
rm -f /tmp/tmp*.mp4
```

## Comparison: S3 Streaming vs Manual Download

| Aspect | S3 Streaming (gemini_s3_analyzer.py) | Manual Download (gemini_physics_analyzer.py) |
|--------|--------------------------------------|----------------------------------------------|
| **Disk usage** | One video at a time (temp only) | All videos stored locally |
| **Setup** | AWS credentials required | No AWS setup needed |
| **Speed** | Slightly slower (S3 download per video) | Faster (download once, process many) |
| **Use case** | Large S3 video libraries | Local video files or small batches |
| **Cleanup** | Automatic | Manual |

## Advanced: Upload Results Back to S3

After processing, you can upload results back to S3:

```bash
# Process videos from S3
python gemini_s3_analyzer.py s3://input-bucket/videos/ --batch

# Upload results to S3
aws s3 sync results_physics/ s3://output-bucket/results/ \
    --exclude "*.mp4" --include "*.json"
```

## Integration with Event Derivation

The output format is identical to `gemini_physics_analyzer.py`, so you can use the same downstream tools:

```bash
# 1. Process from S3
python gemini_s3_analyzer.py s3://bucket/video.mp4

# 2. Validate (same as before)
python validate_physics_output.py results_physics/video_physics.json

# 3. Derive events (same as before)
python physics_to_events.py results_physics/video_physics.json \
    -o results_physics/video_events.json
```

## Full Pipeline Script

Create `process_s3_handball.sh`:

```bash
#!/bin/bash
set -e

S3_PREFIX=$1
OUTPUT_DIR=${2:-results_physics}

if [ -z "$S3_PREFIX" ]; then
    echo "Usage: $0 s3://bucket/prefix/ [output_dir]"
    exit 1
fi

echo "Processing videos from: $S3_PREFIX"
echo "Output directory: $OUTPUT_DIR"
echo

# 1. Analyze physics from S3
python gemini_s3_analyzer.py "$S3_PREFIX" --batch -o "$OUTPUT_DIR" -v

# 2. Validate all outputs
echo
echo "Validating physics outputs..."
for physics_file in "$OUTPUT_DIR"/*_physics.json; do
    if [ -f "$physics_file" ]; then
        python validate_physics_output.py "$physics_file"
    fi
done

# 3. Derive events for all
echo
echo "Deriving events..."
for physics_file in "$OUTPUT_DIR"/*_physics.json; do
    if [ -f "$physics_file" ]; then
        base=$(basename "$physics_file" _physics.json)
        python physics_to_events.py "$physics_file" \
            -o "$OUTPUT_DIR/${base}_events.json"
    fi
done

echo
echo "✅ Pipeline complete!"
echo "Results saved to: $OUTPUT_DIR"
```

Make it executable and run:

```bash
chmod +x process_s3_handball.sh
./process_s3_handball.sh s3://my-bucket/handball-clips/
```
