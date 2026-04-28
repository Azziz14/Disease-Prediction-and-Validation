import sys
import os
import api.routes.assistant_routes as ar
print(f"Assistant Routes Path: {ar.__file__}")

# Check content briefly
with open(ar.__file__, 'r') as f:
    content = f.read()
    print(f"Has [ASSISTANT] log? {'[ASSISTANT]' in content}")
    print(f"Has absolute .env path? {'c:\\Users\\ashis\\Downloads\\prediction' in content}")
