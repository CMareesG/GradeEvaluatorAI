from config import model
import json
import re

def clean_json(response):
    response = re.sub(r"```json|```", "", response).strip()
    return json.loads(response)

def round_to_half(score, max_score):
    # clamp score within valid range
    score = max(0, min(score, max_score))
    return round(score * 2) / 2


def evaluate_answer(q_id, data):
    max_score = data["max_score"]
    keywords = data.get("keywords", [])

    # 🧠 CASE 1: 1-MARK QUESTION (semantic)
    if max_score == 1:
        prompt = f"""
You are a STRICT but fair exam evaluator.

Question:
{data['question']}

Correct Answer:
{data['correct_answer']}

Student Answer:
{data['student_answer']}

Rules:
- If meaning is correct → 1
- If partially correct → 0.5
- If wrong → 0

Return JSON:
{{
  "question_id": "{q_id}",
  "score": number,
  "max_score": 1,
  "feedback": "short explanation"
}}
"""
        response = model.generate_content(prompt)
        result = clean_json(response.text)

        result["score"] = round_to_half(result.get("score", 0), 1)
        return result


    # 🧠 CASE 2: 2-MARK QUESTION (semi-strict)
    elif max_score == 2:
        prompt = f"""
You are a STRICT exam evaluator.

Question:
{data['question']}

Correct Answer:
{data['correct_answer']}

Expected Concepts:
{keywords}

Student Answer:
{data['student_answer']}

Rules:
- Evaluate meaning + concepts
- Missing concepts → reduce marks
- Partial answer → partial marks

Return JSON:
{{
  "question_id": "{q_id}",
  "score": number,
  "max_score": 2,
  "feedback": "what is missing",
  "missing_keywords": []
}}
"""
        response = model.generate_content(prompt)
        result = clean_json(response.text)

        result["score"] = round_to_half(result.get("score", 0), 2)
        return result


    # 🧠 CASE 3: 3+ MARK QUESTIONS (strict)
    else:
        prompt = f"""
You are a STRICT exam evaluator.

Question:
{data['question']}

Correct Answer:
{data['correct_answer']}

Expected Keywords:
{keywords}

Student Answer:
{data['student_answer']}

Rules:
- All key concepts needed for full marks
- Missing concepts → reduce marks proportionally
- Penalize incorrect statements

Return JSON:
{{
  "question_id": "{q_id}",
  "score": number,
  "max_score": {max_score},
  "feedback": "detailed explanation",
  "matched_keywords": [],
  "missing_keywords": []
}}
"""
        response = model.generate_content(prompt)
        result = clean_json(response.text)

        matched = result.get("matched_keywords", [])
        total = len(keywords)

        if total > 0:
            raw_score = (len(matched) / total) * max_score
        else:
            raw_score = result.get("score", 0)

        result["score"] = round_to_half(raw_score, max_score)

        return result