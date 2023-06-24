__version__ = "0.0.0.1"
app_name = "Build my exam"

import streamlit as st
import os
from PyPDF2 import PdfReader
import openai
import functions
import prompt


st.set_page_config(layout='centered', page_title=f'{app_name} {__version__}')
ss = st.session_state


#User's API key to OpenAI
def on_api_key_change():
	api_key = ss.get('api_key') or os.getenv('OPENAI_API_KEY')
	os.environ['OPENAI_API_KEY'] = api_key

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text






def main():
    st.write('## 1. Enter your OpenAI API key')
    st.text_input('OpenAI API key', type='password', key='api_key', on_change=on_api_key_change, label_visibility="collapsed")
    st.write(os.environ['OPENAI_API_KEY'])
    
    
    st.header("Chat with multiple PDFs :books:")
    user_question = st.text_input("Ask a question about your documents:")

    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
        if st.button("Generate Exam"):
             with st.spinner("Processing"):
                  # get pdf text
                  raw_text = get_pdf_text(pdf_docs)
                  # new exam
                  


if __name__ == '__main__':
    main()
