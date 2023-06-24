__version__ = "0.0.0.1"
app_name = "Create my Exam"



import streamlit as st
#from dotenv import load_dotenv


def on_api_key_change():
	api_key = ss.get('api_key') or os.getenv('OPENAI_KEY')
	model.use_key(api_key) # TODO: empty api_key
	#
	if 'data_dict' not in ss: ss['data_dict'] = {} # used only with DictStorage
	ss['storage'] = storage.get_storage(api_key, data_dict=ss['data_dict'])
	ss['cache'] = cache.get_cache()
	ss['user'] = ss['storage'].folder # TODO: refactor user 'calculation' from get_storage
	model.set_user(ss['user'])
	ss['feedback'] = feedback.get_feedback_adapter(ss['user'])
	ss['feedback_score'] = ss['feedback'].get_score()
	#
	ss['debug']['storage.folder'] = ss['storage'].folder
	ss['debug']['storage.class'] = ss['storage'].__class__.__name__


def main():
    st.write('## 1. Enter your OpenAI API key')
    st.text_input('OpenAI API key', type='password', key='api_key', on_change=on_api_key_change, label_visibility="collapsed")
    
    st.header("Chat with multiple PDFs :books:")
    user_question = st.text_input("Ask a question about your documents:")

    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
               

if __name__ == '__main__':
    main()
