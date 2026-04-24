from config import model

def extract_text_from_image(image):
    prompt = """
        You are an OCR system.

        Extract the handwritten text EXACTLY as it appears in the image.

        Rules:
        - Do NOT correct spelling mistakes
        - Do NOT improve grammar
        - Do NOT rephrase sentences
        - Do NOT add missing words
        - Preserve mistakes exactly as written
        - Preserve original structure (Q1, Q2 etc.)
        - If a word is unclear, write it as is or mark with [?]

        Return ONLY the raw extracted text.
    """

    response = model.generate_content([prompt,image])
    return response.text
