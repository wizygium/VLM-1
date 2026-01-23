
import os
from google import genai

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not set")
    exit(1)

client = genai.Client(api_key=api_key)

print("Listing models...")
try:
    models = client.models.list()
    first = True
    for m in models:
        if first:
             print(f"Attributes of first model object: {dir(m)}")
             first = False
        print(f"Model: {m.name}")
        print(f"  DisplayName: {m.display_name}")
        # Try to access supported methods safely if it exists, otherwise skip
        if hasattr(m, 'supported_generation_methods'):
             print(f"  SupportedGenerationMethods: {m.supported_generation_methods}")
        print("-" * 20)
except Exception as e:
    print(f"Error listing models: {e}")
