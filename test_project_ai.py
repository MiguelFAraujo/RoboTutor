import os
import time
from core.ai_tutor import get_response_stream
from dotenv import load_dotenv

load_dotenv()

print("Testing AI Tutor Response Stream...")
try:
    generator = get_response_stream("Hello, assert connection!")
    response_text = ""
    for chunk in generator:
        response_text += chunk
        print(chunk, end="", flush=True)
    
    print("\n\nFull response received successfully.")
except Exception as e:
    print(f"\nCRITICAL ERROR: {e}")
