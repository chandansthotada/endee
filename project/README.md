<h1 align="center">📄 AI-Powered Local PDF Chatbot (RAG)</h1>

<p align="center">
  <strong>An offline, blazing-fast, and privacy-first Retrieval-Augmented Generation (RAG) Chatbot that lets you "talk" to your PDFs. Built with Python, Streamlit, and PyTorch.</strong>
</p>

---

## 🚀 Overview

This application allows users to upload massive PDF documents and interactively query their contents in real-time. Instead of relying on expensive, privacy-invasive cloud APIs like OpenAI, this project runs **100% locally** using a state-of-the-art `SentenceTransformer` model to generate semantic embeddings. It is engineered for maximum performance, featuring intelligent chunking algorithms and a multi-context fusion architecture.

This project was intentionally designed to solve real-world document intelligence problems by combining **Natural Language Processing (NLP)**, **Efficient Information Retrieval**, and a **Reactive User Interface**. 

## ✨ Key Features & Technical Highlights

- **🧠 Local NLP Embeddings**: Utilizes the `all-MiniLM-L6-v2` transformer model via PyTorch to generate high-quality dense vector representations of text. No API keys required, ensuring complete data privacy and zero cost.
- **⚡ Advanced Document Parser & Chunking**: Implementing a custom cleaning heuristic, the app automatically strips out noise (e.g., page numbers, orphaned letters) and bundles text into coherent 3-sentence chunks. This significantly optimizes tensor processing, reducing index times from minutes down to seconds.
- **🔍 Multi-Context Semantic Retrieval**: Calculates Cosine Similarity between the user's query and the document index. Instead of returning just a single snippet, it grabs the **Top 3** semantic matches from entirely different pages, seamlessly merges overlapping context ranges, and reconstructs a cohesive summary answer.
- **🎨 Interactive Chat Memory (UI)**: Built with Streamlit's reactive UI framework (`st.chat_message`, `st.session_state`). Designed to emulate modern AI assistants, it remembers chat history context across the session seamlessly.
- **🛡️ Stateful Lazy-Loading**: Architectural optimizations defer the loading of the 80MB AI model out of the global scope. This prevents blocking the main thread, allowing the web interface to load and respond instantly.

## 🛠️ Tech Stack

- **Language:** Python 3.9+
- **Frontend Framework:** Streamlit
- **Machine Learning / NLP:** PyTorch, Sentence-Transformers (HuggingFace)
- **Document Processing:** PyPDF2
- **Vector Operations:** Tensor/Cosine Similarity Operations (via PyTorch/Torch)

---

## 🎯 How It Works Under the Hood (Step-by-Step)

If you are an interviewer or technical recruiter, here is exactly how the data flows through the application:

### Step 1: Document Upload & Sanitization
When a user uploads a PDF, the app uses `PyPDF2` to extract raw text paragraph-by-paragraph. It applies Regex filters to strip away bad characters, multiple spaces, URLs, and emails.

### Step 2: Intelligent Chunking
Raw text cannot be processed efficiently by AI models. The app splits the text using punctuation marks to identify sentences. To optimize the AI, it strips away "junk" fragments under 10 characters (like stray numbers or bullet points) and tightly **bundles 3 continuous sentences together** into larger "chunks". This slashes the required AI workload by roughly 10x!

### Step 3: Local Vectorization (Embedding)
The pre-processed paragraph chunks are passed into an offline HuggingFace embedding model (`all-MiniLM-L6-v2`) via PyTorch. This converts the human text into mathematical vectors (embeddings) and caches them locally in the session memory.

### Step 4: Semantic Query Search
When the user types a question, the app generates a localized vector for the question alone. It then computes the **Cosine Similarity** between the question's vector and the document's thousands of vector chunks almost instantly.

### Step 5: Multi-Context Fusion & Formatting
The AI isolates the **Top 3** best-matching chunks from the document. Instead of displaying them generically, it pulls the surrounding chunks around the matches, intelligently merges overlapping context blocks to prevent repeating information, and dynamically formats the raw text via Markdown headers and bullets before sending it to the Streamlit Chat UI!

---

## 💻 Installation & Setup

It is extremely simple to get this project running on your local machine.

### 1. Clone the repository
```bash
git clone https://github.com/chandansthotada/endee.git
cd ai-pdf-chatbot
```

### 2. Install dependencies
Ensure you have Python installed, then run:
```bash
pip install -r requirements.txt
```

### 3. Start the application
```bash
streamlit run app.py
```
The application will automatically launch in your browser at `http://localhost:8501`.

---

## 📤 Quick-Start: Uploading this Project to GitHub

If you are looking to fork or upload this project to your own GitHub portfolio, follow these steps:

1. Open your terminal in the project directory.
2. Ensure you have tracked the files via git:
   ```bash
   git init
   git add .
   git commit -m "feat: complete local RAG PDF chatbot"
   ```
3. Create a **New Repository** on github.com (do not select "add a README" since you already have this one).
4. Run the final push commands provided by GitHub:
   ```bash
   git branch -M main
   git remote add origin https://github.com/chandansthotada/endee.git
   git push -u origin main
   ```

I built this project to demonstrate my ability to take complex NLP and Machine Learning concepts and package them into highly optimized, user-friendly software applications.


