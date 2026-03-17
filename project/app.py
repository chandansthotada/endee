if user_question:
    if data_store:
        st.write("Searching from Endee...")
        
        # simple smarter answer
        text = data_store[0]
        
        if user_question.lower() in text.lower():
            st.write("Answer found in document ✅")
        else:
            st.write("Showing related content:")
        
        st.write(text[:300])
    else:
        st.write("No data available. Upload a PDF first.")
