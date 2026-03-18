import re
import streamlit as st
from PyPDF2 import PdfReader

# Page settings
st.set_page_config(page_title="AI PDF Chatbot with Endee", layout="wide")

# Title
st.title("📄 AI PDF Chatbot with Endee")
st.write("Upload a PDF and ask questions from it.")

# Store data (simulate Endee)
if "data_store" not in st.session_state:
    st.session_state.data_store = ""

# Upload PDF
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

# Clean text
def clean_text(text):
    text = "".join(ch if ch.isprintable() else " " for ch in text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# Read PDF
if uploaded_file is not None:
    reader = PdfReader(uploaded_file)
    content = ""

    for page in reader.pages:
        text = page.extract_text()
        if text:
            content += clean_text(text) + " "

    if content:
        st.session_state.data_store = content
        st.success("File stored in Endee (simulated)")
    else:
        st.error("Could not read PDF")

# Ask question
user_question = st.text_input("Ask a question:")

# Improved answer logic
def find_answer(text, question):
    # split better using new lines + sentences
    chunks = re.split(r'\n|\.', text)

    question_words = set(re.findall(r'\w+', question.lower()))

    best_match = ""
    best_score = 0

    for chunk in chunks:
        chunk_lower = chunk.lower()
        chunk_words = set(re.findall(r'\w+', chunk_lower))

        # matching score
        score = len(question_words.intersection(chunk_words))

        # extra weight for full word match
        for word in question_words:
            if word in chunk_lower:
                score += 1

        # prefer longer meaningful text
        if len(chunk.strip()) > 30:
            score += 1

        if score > best_score:
            best_score = score
            best_match = chunk

    return best_match.strip()

# Show answer
if user_question:
    if st.session_state.data_store:
        st.info("Searching from Endee...")
        answer = find_answer(st.session_state.data_store, user_question)

        if answer:
            st.success("Answer:")
            st.write(answer)
        else:
            st.write("No relevant answer found.")
    else:
        st.error("Upload a PDF first.")
