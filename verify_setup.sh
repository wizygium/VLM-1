#!/bin/bash
# Quick verification script for Codespace setup

echo "=== Gemini API Key Setup Verification ==="
echo ""

if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY is NOT set"
    echo ""
    echo "Please:"
    echo "1. Go to: https://github.com/settings/codespaces (or repository settings)"
    echo "2. Add secret: GEMINI_API_KEY = your-key-here"
    echo "3. Rebuild Codespace (Cmd/Ctrl+Shift+P → 'Codespaces: Rebuild Container')"
    exit 1
else
    echo "✓ GEMINI_API_KEY is set (${#GEMINI_API_KEY} characters)"
    echo ""
    echo "Running full API test..."
    python test_gemini_key.py
fi
