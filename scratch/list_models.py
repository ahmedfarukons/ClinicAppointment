import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

try:
    print("Listing models...")
    for m in client.models.list():
        print(f" - {m.name}")
except Exception as e:
    print("List models failed:", e)
