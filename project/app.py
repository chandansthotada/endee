import streamlit as st

st.title("AI PDF Chatbot")

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file is not None:
    st.write("File uploaded successfully!")

    user_question = st.text_input("Ask a question:")

    if user_question:
        st.write("You asked:", user_question)
        st.write("Answer: This is a sample answer (AI part coming next)")
