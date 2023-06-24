__version__ = "0.0.0.1"
app_name = "Build my exam"

import streamlit as st
from dotenv import load_dotenv
import os

st.set_page_config(layout='centered', page_title=f'{app_name} {__version__}')
ss = st.session_state


#User's API key to OpenAI
def on_api_key_change():
	api_key = ss.get('api_key') or os.getenv('OPENAI_API_KEY')
	os.environ['OPENAI_API_KEY'] = api_key



#from dotenv import load_dotenv



def main():
    load_dotenv()
    
    st.header("Chat with multiple PDFs :books:")
    user_question = st.text_input("Ask a question about your documents:")

    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
               

if __name__ == '__main__':
    main()
