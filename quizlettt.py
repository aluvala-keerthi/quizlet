import streamlit as st
import pandas as pd
import random
import time

st.title("Randomized QnA Display App")

# Initialize session state
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False
    st.session_state.questions = None
    st.session_state.progress = {"used_questions": [], "current_index": 0}
    st.session_state.quiz_started = False
    st.session_state.selected_questions = None
    st.session_state.answer_shown = False

# File upload section
if not st.session_state.file_uploaded:
    uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()

        # Filter valid questions
        valid_questions = [
            {"id": i, "question": row["Question"], "answer": row["Answer"]}
            for i, row in df.iterrows()
            if pd.notna(row["Question"]) and str(row["Question"]).strip() != ""
        ]

        if not valid_questions:
            st.error("The uploaded file has no valid questions!")
            st.stop()

        st.session_state.questions = valid_questions
        st.session_state.file_uploaded = True
        st.rerun()

# Ensure questions are loaded
if st.session_state.questions is None:
    st.warning("Please upload an Excel file to start.")
    st.stop()

# Get remaining questions
remaining_questions = [q for q in st.session_state.questions if q["id"] not in st.session_state.progress["used_questions"]]

# Reset quiz state if all questions are done
if not remaining_questions:
    st.success("All questions completed! Please upload a new Excel file.")
    st.session_state.file_uploaded = False
    st.session_state.questions = None
    st.session_state.progress = {"used_questions": [], "current_index": 0}
    st.session_state.quiz_started = False
    st.session_state.selected_questions = None
    st.stop()

# Show quiz settings only if quiz hasn't started
if not st.session_state.quiz_started:
    # Time before answer reveal
    st.session_state.answer_time = st.number_input(
        "Enter time (in seconds) before the answer is revealed:",
        min_value=1, max_value=20, value=5, step=1
    )
    
    # Number of questions
    num_questions = st.number_input(
        "How many questions do you want to attempt?",
        min_value=1,
        max_value=len(remaining_questions),
        value=min(10, len(remaining_questions)),
        step=1
    )
    
    if st.button("Start Quiz"):
        st.session_state.selected_questions = random.sample(remaining_questions, num_questions)
        st.session_state.progress["current_index"] = 0
        st.session_state.answer_shown = False
        st.session_state.start_time = time.time()
        st.session_state.quiz_started = True
        st.rerun()

# Hide settings after quiz starts
if st.session_state.quiz_started:
    st.markdown("<style>div[data-testid='stNumberInput'] {display: none;}</style>", unsafe_allow_html=True)

# Quiz logic
if st.session_state.selected_questions is not None:
    current_index = st.session_state.progress["current_index"]
    
    if current_index >= len(st.session_state.selected_questions):
        # Quiz completed - reset state but keep questions
        st.session_state.progress["used_questions"].extend([q["id"] for q in st.session_state.selected_questions])
        st.session_state.selected_questions = None
        st.session_state.quiz_started = False
        st.session_state.answer_shown = False
        st.success("Quiz completed! You can start a new quiz with the same questions or upload a new file.")
        st.rerun()
    
    current_question = st.session_state.selected_questions[current_index]
    
    # Display question
    question_placeholder = st.empty()
    answer_placeholder = st.empty()
    question_placeholder.markdown(f"### {current_question['question']}")
    
    # Show answer after time elapses
    elapsed_time = time.time() - st.session_state.start_time
    
    
    # Next question button
    btn = st.button("Show Answer / Next Question (Press Space)")


    if btn:
        if not st.session_state.answer_shown:
            # First click - show answer
            st.session_state.answer_shown = True
            answer_placeholder.markdown(f"### **Answer:** {current_question['answer']}")
            # Wait 5 seconds then move to next question
            time.sleep(5)
            st.session_state.answer_shown = False
            st.session_state.progress["current_index"] += 1
            st.session_state.start_time = time.time()
            st.rerun()
        else:
            # Second click - move to next question immediately
            st.session_state.answer_shown = False
            st.session_state.progress["current_index"] += 1
            st.session_state.start_time = time.time()
            st.rerun()

# Spacebar shortcut
st.markdown("""
    <script>
    document.addEventListener("keydown", function(event) {
        if (event.code === "Space") {
            var buttons = document.getElementsByTagName('button');
            if (buttons.length > 0) {
                buttons[0].click();
            }
        }
    });
    </script>
""", unsafe_allow_html=True)