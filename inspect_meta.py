
from google.genai import types
import inspect
try:
    print(inspect.signature(types.VideoMetadata))
    print(types.VideoMetadata.model_fields.keys())
except:
    pass
print(dir(types.VideoMetadata))
