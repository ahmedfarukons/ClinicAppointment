import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

try:
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="Hi",
    )
    print("Direct SDK response:", response.text)
except Exception as e:
    print("Direct SDK failed:", e)
