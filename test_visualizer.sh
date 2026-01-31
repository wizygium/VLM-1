#!/bin/bash
# Test script for physics visualizer

echo "=== Testing Physics Visualizer ==="
echo

# Check Python dependencies
echo "1. Checking Python dependencies..."
python3 -c "import fastapi; print('✓ FastAPI installed')" || echo "✗ FastAPI missing - install with: pip install fastapi"
python3 -c "import uvicorn; print('✓ Uvicorn installed')" || echo "✗ Uvicorn missing - install with: pip install uvicorn"
python3 -c "import boto3; print('✓ Boto3 installed')" || echo "✗ Boto3 missing - install with: pip install boto3"
echo

# Check if port is available
echo "2. Checking port 8001..."
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port 8001 is already in use"
    echo "   Running processes:"
    lsof -Pi :8001 -sTCP:LISTEN
else
    echo "✓ Port 8001 is available"
fi
echo

# Check data directory
echo "3. Checking results directory..."
if [ -d "results_physics" ]; then
    count=$(ls -1 results_physics/*_physics.json 2>/dev/null | wc -l)
    echo "✓ results_physics/ exists with $count physics files"
    ls -lh results_physics/
else
    echo "✗ results_physics/ directory not found"
fi
echo

# Check AWS credentials
echo "4. Checking AWS credentials..."
if [ -f "$HOME/.aws/credentials" ] || [ -n "$AWS_ACCESS_KEY_ID" ]; then
    echo "✓ AWS credentials configured"
else
    echo "⚠️  AWS credentials not found"
    echo "   Run: aws configure"
fi
echo

echo "=== Ready to start server ==="
echo "Run: ./start_visualizer.sh"
echo "Or:  cd physics_visualizer && python3 server.py"
