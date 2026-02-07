#!/bin/bash
# Full pipeline for processing handball videos from S3
# Uses Gemini Cache Analyzer V2 (Stage 1) and Python Inference (Stage 2)

set -e

S3_PREFIX=$1
OUTPUT_DIR=${2:-data/analyses}
TEMP_VIDEO_DIR="data/videos/temp"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

if [ -z "$S3_PREFIX" ]; then
    echo "Usage: $0 s3://bucket/prefix/ [output_dir]"
    echo
    echo "Examples:"
    echo "  # Single video"
    echo "  $0 s3://my-bucket/video.mp4"
    echo
    exit 1
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Handball Video Analysis Pipeline (S3 → Physics → Events)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Input:  $S3_PREFIX"
echo "Output: $OUTPUT_DIR"
echo

# Check env vars
if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "${RED}❌ Error: GEMINI_API_KEY not set${NC}"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"
mkdir -p "$TEMP_VIDEO_DIR"

# Download Logic
VIDEO_FILENAME=$(basename "$S3_PREFIX")
LOCAL_VIDEO="$TEMP_VIDEO_DIR/$VIDEO_FILENAME"

if [[ "$S3_PREFIX" == s3://* ]]; then
    echo -e "${BLUE}[Download] Fetching from S3...${NC}"
    aws s3 cp "$S3_PREFIX" "$LOCAL_VIDEO" || { echo -e "${RED}Failed to download${NC}"; exit 1; }
else
    # Assume local path provided
    LOCAL_VIDEO="$S3_PREFIX"
fi

# Step 1: Physics Analysis (VLM)
echo -e "${BLUE}[Stage 1] Physics Observation (16fps)${NC}"
python gemini_cache_analyzer_v2.py "$LOCAL_VIDEO" --output "$OUTPUT_DIR" --verbose

# Step 2: Event Derivation
echo -e "${BLUE}[Stage 2] Event Inference${NC}"
PHYSICS_JSON="$OUTPUT_DIR/${VIDEO_FILENAME%.*}_physics.json"
EVENTS_JSON="$OUTPUT_DIR/${VIDEO_FILENAME%.*}_events.json"

if [ -f "$PHYSICS_JSON" ]; then
    python physics_to_events.py "$PHYSICS_JSON" --output "$EVENTS_JSON" --verbose
else
    echo -e "${RED}Physics file not found: $PHYSICS_JSON${NC}"
    exit 1
fi

# Cleanup
if [[ "$S3_PREFIX" == s3://* ]]; then
    echo -e "${BLUE}[Cleanup] Removing temp video...${NC}"
    rm "$LOCAL_VIDEO"
fi

echo -e "${GREEN}✅ Pipeline Complete! Results in $OUTPUT_DIR${NC}"

