import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key prefix: {api_key[:10]}...")

try:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)
    res = llm.invoke("Hi")
    print("Response with gemini-1.5-flash:", res.content)
except Exception as e:
    print("Failed with gemini-1.5-flash:", e)

try:
    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key)
    res = llm.invoke("Hi")
    print("Response with gemini-pro:", res.content)
except Exception as e:
    print("Failed with gemini-pro:", e)
