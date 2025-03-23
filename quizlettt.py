import streamlit as st
import pandas as pd
import random
import time

st.title("Randomized QnA Display App")

# **Step 1: Handle File Upload**
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False
    st.session_state.questions = None
    st.session_state.progress = {"used_questions": [], "current_index": 0}

uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx", "xls"])

if uploaded_file is not None and not st.session_state.file_uploaded:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    # **Filter valid questions**
    st.session_state.questions = [
        {"id": i, "question": row["Question"], "answer": row["Answer"]}
        for i, row in df.iterrows()
        if pd.notna(row["Question"]) and str(row["Question"]).strip() != ""
    ]

    if not st.session_state.questions:
        st.error("The uploaded file has no valid questions!")
        st.stop()

    st.session_state.file_uploaded = True  # Mark file as uploaded

# **Stop if no file uploaded yet**
if not st.session_state.file_uploaded:
    st.warning("Please upload an Excel file to start.")
    st.stop()

# **Step 2: Get Remaining Questions**
remaining_questions = [q for q in st.session_state.questions if q["id"] not in st.session_state.progress["used_questions"]]

# **If all questions are done, ask for a new file**
if not remaining_questions:
    st.success("All questions completed! Please upload a new Excel file.")
    st.session_state.file_uploaded = False  # Reset upload state
    st.session_state.questions = None
    st.session_state.progress = {"used_questions": [], "current_index": 0}
    st.stop()

# **Step 3: Allow User to Choose Number of Questions**
if "selected_questions" not in st.session_state or st.session_state.selected_questions is None:
    num_questions = st.number_input(
        "How many questions do you want to attempt?",
        min_value=1,
        max_value=len(remaining_questions),
        value=10,
        step=1
    )
    if st.button("Start Quiz"):
        st.session_state.selected_questions = random.sample(remaining_questions, num_questions)
        st.session_state.progress["current_index"] = 0
        st.rerun()

if "selected_questions" not in st.session_state or st.session_state.selected_questions is None:
    st.stop()

# **Step 4: Get Current Question**
current_index = st.session_state.progress["current_index"]

if current_index >= len(st.session_state.selected_questions):
    st.success("Quiz completed! Restarting...")
    st.session_state.progress["used_questions"].extend([q["id"] for q in st.session_state.selected_questions])
    st.session_state.selected_questions = None
    st.session_state.progress["current_index"] = 0
    time.sleep(2)
    st.rerun()

current_question = st.session_state.selected_questions[current_index]

# **Step 5: Display Question & Answer**
question_placeholder = st.empty()
question_placeholder.markdown(f"### {current_question['question']}")

if "answer_shown" not in st.session_state:
    st.session_state.answer_shown = False

if not st.session_state.answer_shown:
    time.sleep(5)
    st.session_state.answer_shown = True
    question_placeholder.markdown(f"### {current_question['question']}\n\n**Answer:** {current_question['answer']}")

# **Step 6: Next Question Button**
if st.button("Next Question"):
    st.session_state.answer_shown = False
    st.session_state.progress["current_index"] += 1
    st.rerun()
