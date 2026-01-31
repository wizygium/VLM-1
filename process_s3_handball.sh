#!/bin/bash
# Full pipeline for processing handball videos from S3

set -e

S3_PREFIX=$1
OUTPUT_DIR=${2:-results_physics}

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
    echo "  # Batch process directory"
    echo "  $0 s3://my-bucket/handball-clips/"
    echo
    echo "  # Custom output directory"
    echo "  $0 s3://my-bucket/videos/ custom_results/"
    exit 1
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Handball Video Analysis Pipeline (S3 → Physics → Events)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo
echo "Input:  $S3_PREFIX"
echo "Output: $OUTPUT_DIR"
echo

# Check for required environment variables
if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "${RED}❌ Error: GEMINI_API_KEY not set${NC}"
    echo "Please set your Gemini API key:"
    echo "  export GEMINI_API_KEY='your-key-here'"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &>/dev/null; then
    echo -e "${RED}❌ Error: AWS credentials not configured${NC}"
    echo "Please configure AWS credentials:"
    echo "  aws configure"
    exit 1
fi

echo -e "${GREEN}✓ Gemini API key configured${NC}"
echo -e "${GREEN}✓ AWS credentials configured${NC}"
echo

# Determine if batch or single video
BATCH_FLAG=""
if [[ "$S3_PREFIX" == */ ]] || [[ "$S3_PREFIX" != *.mp4 ]]; then
    BATCH_FLAG="--batch"
    echo -e "${BLUE}Mode: Batch processing (all .mp4 files in prefix)${NC}"
else
    echo -e "${BLUE}Mode: Single video${NC}"
fi
echo

# Step 1: Physics Analysis
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Step 1: Physics Observation (VLM)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

python gemini_s3_analyzer.py "$S3_PREFIX" $BATCH_FLAG -o "$OUTPUT_DIR" -v

# Step 2: Validation
echo
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Step 2: Validating Physics Outputs${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

VALIDATION_FAILED=0
for physics_file in "$OUTPUT_DIR"/*_physics.json; do
    if [ -f "$physics_file" ]; then
        echo "Validating $(basename "$physics_file")..."
        if python validate_physics_output.py "$physics_file"; then
            echo -e "${GREEN}✓ Validation passed${NC}"
        else
            echo -e "${RED}✗ Validation failed${NC}"
            VALIDATION_FAILED=1
        fi
        echo
    fi
done

# Step 3: Event Derivation
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Step 3: Deriving Events (Programmatic)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

for physics_file in "$OUTPUT_DIR"/*_physics.json; do
    if [ -f "$physics_file" ]; then
        base=$(basename "$physics_file" _physics.json)
        echo "Deriving events for $base..."
        python physics_to_events.py "$physics_file" \
            -o "$OUTPUT_DIR/${base}_events.json" -v
        echo
    fi
done

# Step 4: Statistics Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Step 4: Statistics Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

for physics_file in "$OUTPUT_DIR"/*_physics.json; do
    if [ -f "$physics_file" ]; then
        echo -e "${BLUE}$(basename "$physics_file")${NC}"
        python physics_to_events.py "$physics_file" --stats
        echo
    fi
done

# Final Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Pipeline Complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo
echo "Results saved to: $OUTPUT_DIR"
echo
echo "Output files:"
ls -lh "$OUTPUT_DIR"/*.json 2>/dev/null || echo "  (no JSON files found)"
echo

if [ $VALIDATION_FAILED -eq 1 ]; then
    echo -e "${RED}⚠️  Warning: Some validation checks failed${NC}"
    echo "Review the validation output above for details"
    exit 1
else
    echo -e "${GREEN}✅ All validation checks passed!${NC}"
fi
