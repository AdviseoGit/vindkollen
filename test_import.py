import os
import sys

print("Testing import...")
try:
    from fastapi.responses import RedirectResponse
    print("Success")
except Exception as e:
    print(f"Error: {e}")
