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

    # Squeeze spaces but preserve newlines
    text = re.sub(r"[ \t]{2,}", " ", text)

    # Auto-format headings for numbers (e.g., " 1. ", " 2. ")
    text = re.sub(r'\s+(\d+\.)\s+([A-Z])', r'\n\n### \1 \2', text)

    # Auto-format questions
    text = re.sub(r'([A-Z][^.?!\n]*\?)', r'\n\n**\1**\n\n', text)

    # Auto-format lists for words followed by a colon (e.g., " products : ")
    text = re.sub(r'\s+([a-zA-Z0-9_-]+)\s*:\s*(?=[a-z])', r'\n- **\1**: ', text)

    # Specific terms seen in PDF
    text = re.sub(r'(Key Components)', r'\n\n#### \1\n', text)

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

# Split text into chunks to speed up AI indexing
def split_into_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+|\n+', text)
    # Filter out tiny strings (like page numbers or single words) that ruin AI padding length
    valid_sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    chunks = []
    # Combine every 3 sentences into a chunk to reduce AI processing time by 3x-10x
    for i in range(0, len(valid_sentences), 3):
        chunk = " ".join(valid_sentences[i:i+3])
        chunks.append(chunk)
    return chunks

# Read PDF content
if uploaded_file is not None:
    # Only process if it's a new file upload
    if "current_file" not in st.session_state or st.session_state.current_file != uploaded_file.name:
        with st.spinner("Processing PDF and building AI Index... (this only happens once)"):
            st.session_state.current_file = uploaded_file.name
            reader = PdfReader(uploaded_file)
            content = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    content += clean_text(text) + " "
            
            if content:
                st.session_state.data_store = content
                sentences = split_into_sentences(content)
                st.session_state.sentences = sentences
                
                # Load model only when needed to prevent blocking UI load
                model = load_model()
                st.session_state.sentence_embeddings = model.encode(sentences, convert_to_tensor=True)
                st.success("PDF processed successfully ✅")
            else:
                st.error("Could not read PDF")

# Store chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "expander" in msg:
            with st.expander("Show AI Matches & Scores"):
                st.markdown(msg["expander"])

# AI-based answer function
def find_answer(question):
    if not question.strip():
        return "", []
    
    sentences = st.session_state.get("sentences", [])
    sentence_embeddings = st.session_state.get("sentence_embeddings", None)
    
    if not sentences or sentence_embeddings is None:
        return "", []

    # Convert question to embeddings (extremely fast)
    model = load_model()
    question_embedding = model.encode(question, convert_to_tensor=True)

    # Compute similarity
    scores = util.cos_sim(question_embedding, sentence_embeddings)[0]

    # Get top 3 matches to provide "every answer" spanning different sections
    top_k = torch.topk(scores, k=min(3, len(scores)))
    valid_indices = [int(idx) for idx in top_k.indices if float(scores[int(idx)]) >= 0.3]
    
    if not valid_indices:
        return "No relevant answer found. Try a clearer question.", []

    # Extract ranges of +/- 1 chunk around each match since chunks are already 3 sentences long
    ranges = []
    for idx in valid_indices:
        start = max(0, idx - 1)
        end = min(len(sentences), idx + 2)
        ranges.append((start, end))
        
    # Merge overlapping ranges so we don't repeat text
    ranges.sort()
    merged_ranges = []
    for r in ranges:
        if not merged_ranges:
            merged_ranges.append(r)
        else:
            last = merged_ranges[-1]
            if r[0] <= last[1]: # overlap
                merged_ranges[-1] = (last[0], max(last[1], r[1]))
            else:
                merged_ranges.append(r)

    # Construct the final answer blocks
    answer_blocks = []
    for start, end in merged_ranges:
        context = sentences[start:end]
        block = "\n\n".join(context)
        block = sanitize_answer(block)
        answer_blocks.append(block)

    # Combine blocks with a visual separator
    answer = "\n\n---\n\n".join(answer_blocks)

    top_sentences = [
        (float(score), sentences[idx])
        for score, idx in zip(top_k.values, top_k.indices)
    ]
    return answer, top_sentences

# Detect if text looks like code
def is_code(text):
    keywords = ["#include", "int main", "class ", "def ", "{", "}", ";", "System.out.println"]
    return any(k in text for k in keywords)

# User question input via chat interface
if user_question := st.chat_input("Ask a question about the PDF:"):
    if st.session_state.get("data_store"):
        # Display user message in chat message container
        st.session_state.messages.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)
            
        # Display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Searching..."):
                answer, top_sentences = find_answer(user_question)
                
                if answer:
                    display_content = "**Answer from PDF:**\n\n" + answer
                    
                    if is_code(answer):
                        display_content += f"\n\n```cpp\n{format_code(answer)}\n```"
                        
                    st.markdown(display_content)
                    
                    # Top matching sentences in expander
                    top_matches_text = ""
                    for i, (score, sent) in enumerate(top_sentences, 1):
                        formatted_sent = sanitize_answer(sent)
                        top_matches_text += f"\n**{i}. (score={score:.3f})**\n{formatted_sent}\n"
                        
                    with st.expander("Show AI Matches & Scores"):
                        st.markdown(top_matches_text)
                        
                    # Save to chat history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": display_content, 
                        "expander": top_matches_text
                    })
                else:
                    msg = "No relevant answer found. Try rephrasing."
                    st.warning(msg)
                    st.session_state.messages.append({"role": "assistant", "content": msg})
    else:
        st.error("Please upload a PDF first.")
