#!/bin/bash
# Copy test zone display files to results_physics for easy testing

echo "Copying test zone display files to results_physics/..."

# Create results_physics if it doesn't exist
mkdir -p results_physics

# Copy all test files
cp test_zone_display/TEST-*.json results_physics/

# Count files
count=$(ls test_zone_display/TEST-*.json 2>/dev/null | wc -l)

echo "✓ Copied $count test files"
echo ""
echo "Test files available:"
ls -1 results_physics/TEST-*.json | sed 's|results_physics/||' | sed 's|_physics.json||'
echo ""
echo "Start the visualizer and select these from the dropdown to test zone display."
echo ""
echo "To start visualizer:"
echo "  cd physics_visualizer && python3 server.py"
echo ""
echo "Then open: http://127.0.0.1:8001"
