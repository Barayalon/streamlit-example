import streamlit as st
#from dotenv import load_dotenv


def main():



st.header("Chat with multiple PDFs :books:")
user_question = st.text_input("Ask a question about your documents:")

with st.sidebar:
    st.subheader("Your documents")
    pdf_docs = st.file_uploader(
        "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
               

if __name__ == '__main__':
    main()
