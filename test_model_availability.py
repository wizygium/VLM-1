
import os
import sys

# Try to import google.genai, if not available, we might need to install it
try:
    from google import genai
except ImportError:
    print("Error: `google.genai` module not found. Please install the Google Gen AI SDK.")
    print("pip install google-genai")
    sys.exit(1)

def load_env(env_path=".env"):
    """Simple .env loader"""
    try:
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")
    except FileNotFoundError:
        print(f"Warning: {env_path} not found.")

def main():
    # Load API Key
    load_env()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env or environment variables.")
        return

    print(f"Using API Key: {api_key[:8]}...")

    try:
        client = genai.Client(api_key=api_key)

        # Discover available models
        print("\nAvailable Models (supporting video):")
        try:
            for model in client.models.list():
                # Check for video support - newer SDK might have different field names structure
                # The user provided snippet: if 'video' in model.supported_generation_methods:
                # We will print all and inspect
                
                methods = getattr(model, 'supported_generation_methods', [])
                # Some models might not have this field populated as expected in preview SDKs
                
                print(f"- {model.name} (Methods: {methods})")
        except Exception as e:
            print(f"Error listing models: {e}")

        # List already uploaded files
        print("\nYour AI Studio Resources:")
        try:
            for f in client.files.list():
                print(f"File Name: {f.display_name}, URI: {f.uri}")
        except Exception as e:
            print(f"Error listing files: {e}")
            
    except Exception as e:
        print(f"Client initialization error: {e}")

if __name__ == "__main__":
    main()
