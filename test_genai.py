import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print(f"API Key present: {bool(api_key)}")
if api_key:
    print(f"API Key start: {api_key[:5]}...")

client = genai.Client(api_key=api_key)

print("\nAttempting to generate content with gemini-2.0-flash-lite...")
try:
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents="Say Hello"
    )
    print(f"Success! Response: {response.text}")
except Exception as e:
    print(f"Error (gemini-2.0-flash-lite): {e}")

print("\nAttempting to generate content with gemini-1.5-flash...")
try:
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="Say Hello"
    )
    print(f"Success! Response: {response.text}")
except Exception as e:
    print(f"Error (gemini-1.5-flash): {e}")
