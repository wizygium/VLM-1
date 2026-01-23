
from google import genai
from google.genai import types
import inspect

print("--- types.VideoMetadata ---")
try:
    print(inspect.signature(types.VideoMetadata))
    print(dir(types.VideoMetadata))
except Exception as e:
    print(e)
    
print("\n--- types.GenerateContentConfig ---")
try:
    print(inspect.signature(types.GenerateContentConfig))
except Exception as e:
    print(e)

print("\n--- types.Part ---")
try:
    print(inspect.signature(types.Part))
except Exception as e:
    print(e)
