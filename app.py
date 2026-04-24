import streamlit as st
import json

from services.pdf_service import convert_pdf_to_images
from services.ocr_service import extract_text_from_image
from services.splitter_service import split_answers
from services.rag_service import build_rag_data
from services.evaluation_service import evaluate_answer

POPPLER_PATH = r"C:/Users/maree/Downloads/Release-25.12.0-0/poppler-25.12.0/Library/bin"

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Evaluation System", layout="wide")

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>

/* Container spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    padding-left: 4rem;
    padding-right: 4rem;
}

/* Section titles */
.section-title {
    font-size: 26px;
    font-weight: 600;
    margin-top: 20px;
    margin-bottom: 10px;
}

/* CARD (FIXED HERE) */
.card {
    padding: 20px;
    border-radius: 12px;
    border: 1px solid rgba(200, 200, 200, 0.3);
    margin-bottom: 20px;

    /* 👇 IMPORTANT CHANGE */
    background-color: rgba(255, 255, 255, 0.04);  /* subtle transparent */
    backdrop-filter: blur(6px);
}

/* METRIC CARD (FIXED) */
.metric-card {
    padding: 15px;
    border-radius: 10px;
    text-align: center;

    /* 👇 adaptive background */
    background-color: rgba(255, 255, 255, 0.06);
}

/* Small text */
.small-text {
    color: rgba(120,120,120,0.9);
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)


# ---------- LOAD DATA ----------
with open("data/answer_keys.json", "r") as f:
    ANSWER_KEYS = json.load(f)

# ---------- HEADER ----------
st.markdown("<div class='section-title'>Handwritten Answer Evaluation System</div>", unsafe_allow_html=True)
st.markdown("<div class='small-text'>Upload handwritten answer sheets and evaluate responses with structured scoring.</div>", unsafe_allow_html=True)

st.write("")

# ---------- FILE UPLOAD ----------
uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file:

    # ---------- STEP 1 ----------
    st.markdown("<div class='section-title'>Document Processing</div>", unsafe_allow_html=True)

    images = convert_pdf_to_images(uploaded_file, POPPLER_PATH)

    col1, col2 = st.columns([1, 3])
    col1.markdown(f"<div class='metric-card'><b>{len(images)}</b><br>Pages</div>", unsafe_allow_html=True)
    col2.markdown("<div class='card'>Document loaded and ready for processing.</div>", unsafe_allow_html=True)

    # ---------- STEP 2 ----------
    st.markdown("<div class='section-title'>Text Extraction</div>", unsafe_allow_html=True)

    progress = st.progress(0)
    full_text = ""

    for i, img in enumerate(images):
        text = extract_text_from_image(img)
        full_text += text + "\n"
        progress.progress((i + 1) / len(images))

    with st.expander("View Extracted Text"):
        st.text(full_text)

    # ---------- STEP 3 ----------
    st.markdown("<div class='section-title'>Answer Structuring</div>", unsafe_allow_html=True)

    student_answers = split_answers(full_text)

    with st.expander("View Structured Answers"):
        for q, ans in student_answers.items():
            st.markdown(f"**{q}**")
            st.text(ans)

    # ---------- STEP 4 ----------
    st.markdown("<div class='section-title'>Reference Mapping</div>", unsafe_allow_html=True)

    rag_data = build_rag_data(student_answers)

    with st.expander("View Retrieved Data"):
        st.json(rag_data)

    # ---------- STEP 5 ----------
    st.markdown("<div class='section-title'>Evaluation</div>", unsafe_allow_html=True)

    results = []
    total_score = 0
    max_total = 0

    for q_id, data in rag_data.items():
        if "error" not in data:
            try:
                result = evaluate_answer(q_id, data)
            except Exception as e:
                result = {
                    "question_id": q_id,
                    "score": 0,
                    "max_score": data["max_score"],
                    "feedback": f"Error: {str(e)}",
                    "matched_keywords": [],
                    "missing_keywords": data["keywords"]
                }

            results.append(result)
            total_score += result["score"]
            max_total += result["max_score"]

    # ---------- SUMMARY ----------
    st.markdown("<div class='section-title'>Summary</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    col1.markdown(f"<div class='metric-card'><b>{total_score}</b><br>Total Score</div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='metric-card'><b>{max_total}</b><br>Maximum</div>", unsafe_allow_html=True)
    percentage = round((total_score/max_total)*100, 2) if max_total else 0
    col3.markdown(f"<div class='metric-card'><b>{percentage}%</b><br>Percentage</div>", unsafe_allow_html=True)

    # ---------- RESULTS ----------
    # ---------- RESULTS ----------
    st.markdown("## Detailed Evaluation")

    for r in results:
        
        with st.container():

            col1, col2 = st.columns([1, 5])

            # LEFT SIDE (Score)
            with col1:
                st.markdown(f"""
                <div style="
                    padding: 12px;
                    border-radius: 8px;
                    border: 1px solid rgba(150,150,150,0.2);
                    text-align: center;
                ">
                    <div style="font-size:18px; font-weight:600;">{r['question_id']}</div>
                    <div style="margin-top:8px; font-size:16px;">
                        {r['score']} / {r['max_score']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # RIGHT SIDE (Feedback)
            with col2:
                st.markdown(f"""
                <div style="
                    padding: 14px;
                    border-radius: 8px;
                    border: 1px solid rgba(150,150,150,0.2);
                ">
                    <div style="font-weight:600; margin-bottom:6px;">
                        Feedback
                    </div>
                    <div style="color: rgba(200,200,200,0.9);">
                        {r['feedback']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if r.get("missing_keywords"):
                    st.markdown(f"""
                    <div style="
                        margin-top:8px;
                        padding:10px;
                        border-radius:6px;
                        border: 1px solid rgba(255,100,100,0.3);
                    ">
                        <b>Missing Concepts:</b><br>
                        {", ".join(r["missing_keywords"])}
                    </div>
                    """, unsafe_allow_html=True)

                if r.get("matched_keywords"):
                    st.markdown(f"""
                    <div style="
                        margin-top:6px;
                        padding:10px;
                        border-radius:6px;
                        border: 1px solid rgba(100,255,100,0.3);
                    ">
                        <b>Covered Concepts:</b><br>
                        {", ".join(r["matched_keywords"])}
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("---")