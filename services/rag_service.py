import json

# Load once
with open("data/answer_keys.json", "r") as f:
    ANSWER_KEYS = json.load(f)


def get_answer_key(q_id):
    """
    Retrieve answer key for given question ID
    """
    return ANSWER_KEYS.get(q_id)


def build_rag_data(student_answers):
    """
    Combine student answers with answer key
    """
    rag_data = {}

    for q_id, student_ans in student_answers.items():
        answer_data = get_answer_key(q_id)

        if answer_data:
            rag_data[q_id] = {
                "question": answer_data["question"],
                "correct_answer": answer_data["answer"],
                "keywords": answer_data.get("keywords", []),
                "max_score": answer_data["max_score"],
                "student_answer": student_ans
            }
        else:
            # handle missing key
            rag_data[q_id] = {
                "student_answer": student_ans,
                "error": "Answer key not found"
            }

    return rag_data