from config import model
import json
import re

def split_answers(full_text):
    prompt = f"""
You are a system that structures exam answers.

Task:
Split answers into Q1, Q2, Q3... Q7.

IMPORTANT:
- Detect question numbers like Q1, Q2 OR 1), 2), 3)
- If numbering changes format, still separate correctly
- Do NOT merge multiple answers into one
- Ensure Q6 and Q7 are separate

Return STRICT JSON only:
{{
  "Q1": "...",
  "Q2": "...",
  "Q3": "...",
  "Q4": "...",
  "Q5": "...",
  "Q6": "...",
  "Q7": "..."
}}

Text:
{full_text}
"""

    response = model.generate_content(prompt)
    raw_output = response.text

    # 🧹 Clean JSON (remove ```json etc.)
    cleaned = re.sub(r"```json|```", "", raw_output).strip()

    try:
        return json.loads(cleaned)
    except:
        print("⚠️ JSON parsing failed. Raw output:")
        print(cleaned)
        return {}