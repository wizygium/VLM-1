#!/usr/bin/env python3
"""
Quick test script to verify Gemini API key is configured correctly.
"""

import os
from pathlib import Path
from google import genai

def test_gemini_key():
    # Check for API key in environment (Codespace secrets have priority)
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        # Fallback: Load .env file if present
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            print(f"No environment variable found. Loading from {env_path}")
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        if key.strip() == "GEMINI_API_KEY" and not os.getenv("GEMINI_API_KEY"):
                            os.environ[key.strip()] = value.strip()
            api_key = os.getenv("GEMINI_API_KEY")
    else:
        print("✓ Using GEMINI_API_KEY from environment (Codespace secret or system env)")

    if not api_key or api_key == "your-api-key-here":
        print("❌ ERROR: GEMINI_API_KEY not set or still has placeholder value")
        print("\nPlease:")
        print("1. Get your API key from: https://aistudio.google.com/apikey")
        print("2. Open .env file and replace 'your-api-key-here' with your actual key")
        return False

    print(f"✓ API key found (length: {len(api_key)} chars)")

    # Test the connection
    try:
        print("\nTesting connection to Gemini API...")
        client = genai.Client(api_key=api_key)

        print("✓ Successfully connected to Gemini API!")

        # List available models
        print("\nListing available models...")
        models = client.models.list()
        print("\nAvailable models for video/image analysis:")
        for model in models:
            if 'gemini' in model.name.lower() and 'vision' not in model.name.lower():
                print(f"  - {model.name}")

        # Simple text generation test with a valid model
        print("\nTesting content generation with gemini-2.5-flash...")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents='Say "Hello from Gemini!" and nothing else.'
        )

        print(f"\n✓ Test generation successful!")
        print(f"Response: {response.text}")

        print("\n✅ All checks passed! Your Gemini API key is configured correctly.")
        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nPossible issues:")
        print("- Invalid API key")
        print("- API key doesn't have required permissions")
        print("- Network connectivity issues")
        return False

if __name__ == "__main__":
    test_gemini_key()
