import re
import streamlit as st
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer, util
import torch

# Page settings
st.set_page_config(page_title="AI PDF Chatbot with Endee", layout="wide")

# Title
st.title("📄 AI PDF Chatbot with Endee")
st.write("Upload a PDF and ask questions from it.")

# Store data
if "data_store" not in st.session_state:
    st.session_state.data_store = ""

# Load AI model (cached for performance)
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

# Upload PDF
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

# Clean text from PDF
def clean_text(text):
    text = "".join(ch if ch.isprintable() else " " for ch in text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\S+@\S+", "", text)
    text = re.sub(r"http[s]?://\S+", "", text)
    return text.strip()

# Format normal text (examples, notes, classes, attributes)
def sanitize_answer(text):
    text = re.sub(r"\S+@\S+", "", text)
    text = re.sub(r"http[s]?://\S+", "", text)
    text = re.sub(r"\s{2,}", " ", text)

    # Line breaks after sentences
    text = re.sub(r'\.\s+', '.\n\n', text)

    # Break key sections
    text = re.sub(r'(Example\s*\d+:)', r'\n\n🔹 \1', text)
    text = re.sub(r'(NOTE:)', r'\n\n⚠️ \1', text)
    text = re.sub(r'(C\+\+ Code|Java Code|Python Code)', r'\n\n💻 \1\n', text)

    # Classes / Objects formatting
    text = re.sub(r'(Class\s+)', r'\n\n📘 Class ', text)
    text = re.sub(r'(Object\s+)', r'\n\n📦 Object ', text)

    # Attributes & Behaviors
    text = re.sub(r'(Attributes\s*\(.*?\))', r'\n- \1', text)
    text = re.sub(r'(Behaviors\s*\(.*?\))', r'\n- \1', text)

    return text.strip()

# Format code snippets nicely
def format_code(text):
    # Line break after semicolon
    text = text.replace(";", ";\n")
    # Line break around braces
    text = text.replace("{", "{\n")
    text = text.replace("}", "\n}\n")
    # Remove multiple blank lines
    text = re.sub(r'\n{2,}', '\n', text)
    return text.strip()

# Split text into sentences
def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+|\n+', text)
    return [s.strip() for s in sentences if s.strip()]

# Read PDF content
if uploaded_file is not None:
    reader = PdfReader(uploaded_file)
    content = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            content += clean_text(text) + " "
    if content:
        st.session_state.data_store = content
        st.success("PDF processed successfully ✅")
    else:
        st.error("Could not read PDF")

# User question input
user_question = st.text_input("Ask a question:")

# AI-based answer function
def find_answer(text, question):
    if not question.strip():
        return "", []
    sentences = split_into_sentences(text)
    if not sentences:
        return "", []

    # Convert to embeddings
    sentence_embeddings = model.encode(sentences, convert_to_tensor=True)
    question_embedding = model.encode(question, convert_to_tensor=True)

    # Compute similarity
    scores = util.cos_sim(question_embedding, sentence_embeddings)[0]

    best_idx = int(torch.argmax(scores))
    best_score = float(scores[best_idx])

    if best_score < 0.3:
        return "No relevant answer found. Try a clearer question.", []

    # Include context
    context = []
    if best_idx > 0:
        context.append(sentences[best_idx - 1])
    context.append(sentences[best_idx])
    if best_idx < len(sentences) - 1:
        context.append(sentences[best_idx + 1])

    answer = " ".join(context)
    answer = sanitize_answer(answer)

    # Top matches
    top_k = torch.topk(scores, k=min(5, len(scores)))
    top_sentences = [
        (float(score), sentences[idx])
        for score, idx in zip(top_k.values, top_k.indices)
    ]
    return answer[:2000], top_sentences  # Show larger snippets

# Detect if text looks like code
def is_code(text):
    keywords = ["#include", "int main", "class ", "def ", "{", "}", ";", "System.out.println"]
    return any(k in text for k in keywords)

# Display answer
if user_question:
    if st.session_state.data_store:
        st.info("Searching using AI... 🤖")
        answer, top_sentences = find_answer(st.session_state.data_store, user_question)
        if answer:
            st.success("Answer from PDF:")

            # Show as formatted code if detected
            if is_code(answer):
                st.code(format_code(answer), language='cpp')  # C++ default, works for Java too
            else:
                st.markdown(answer)

            # Top matching sentences
            st.markdown("### 🔍 Top matching sentences:")
            for i, (score, sent) in enumerate(top_sentences, 1):
                formatted_sent = sanitize_answer(sent)
                st.markdown(f"**{i}. (score={score:.3f})**  \n{formatted_sent}")

        else:
            st.warning("No relevant answer found. Try rephrasing.")
    else:
        st.error("Please upload a PDF first.")
