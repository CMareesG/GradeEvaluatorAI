import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("API_KEY")
genai.configure(api_key=os.getenv("API_KEY"))

model = genai.GenerativeModel("gemini-3.1-flash-lite-preview")
