import streamlit as st

st.title("AI PDF Chatbot with Endee")

# Dummy data to simulate vector storage
data_store = []

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file is not None:
    content = uploaded_file.read().decode("latin-1")
    
    # Store data (simulating Endee)
    data_store.append(content)
    
    st.write("File stored in Endee (simulated)")

user_question = st.text_input("Ask a question:")

if user_question:
    if data_store:
        st.write("Searching from Endee...")
        st.write("Answer:", data_store[0][:200])  # show part of stored text
    else:
        st.write("No data available. Upload a PDF first.")
