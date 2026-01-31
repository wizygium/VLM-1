#!/bin/bash
# Start the Handball Physics Visualizer

echo "Starting Handball Physics Visualizer..."
echo
echo "The visualizer will be available at:"
echo "  http://127.0.0.1:8001"
echo
echo "Press Ctrl+C to stop"
echo

cd physics_visualizer && python server.py
